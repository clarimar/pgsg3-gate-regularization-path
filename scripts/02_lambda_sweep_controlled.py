#!/usr/bin/env python
"""Lambda regularization path under the corrected protocol.

WHAT CHANGED FROM `01_lambda_sweep.py`
--------------------------------------
Four controls, each forced by a result of the programme that post-dates the
August 2026 sweeps. The earlier script is kept as the record of what was run
then; it is not a substitute for this one.

1. GROUPED SPLIT. The 1,448 NIR spectra of season 4 come from 725 fruits,
   723 measured twice. The earlier random split put both spectra of a fruit
   on opposite sides. Splits here are over whole fruits.

2. FIXED STEP BUDGET. With early stopping the number of steps varied 246-499
   across seeds and lambdas, and the displacement of a saturated gate is
   proportional to the number of steps, so part of any effect attributed to
   lambda was step count. Every run here takes exactly `--epochs` steps and
   the FINAL state is measured.

3. OPTIMIZER AS A DECLARED VARIABLE. Adam applies weight decay as a coupled
   L2 term, which drives saturated gates at a rate set by the learning rate;
   AdamW decouples it. The choice changes what the fitted gate means, so it
   is swept rather than assumed.

4. A NON-CIRCULAR RELEVANCE REFERENCE. rho(gate, prior) measures adherence
   to the starting point, which lambda controls by construction, so it cannot
   tell whether the gate is RIGHT. Agreement with the absolute coefficients
   of a PLS calibrated on the training partition is a reference derived from
   the data instead.

PRE-REGISTRATION
----------------
H0 is evaluated by the criterion fixed in `docs/protocolo_hipoteses.md`
BEFORE any run: rho < 0.95 AND R^2 within one SD of the best AND
Jaccard >= 0.90. The agreement-with-PLS axis was added in October 2026,
after those sweeps, and is reported as EXPLORATORY. It is not used to
declare H0 supported.

USAGE
-----
    export PGSG1_ROOT=~/Dropbox/pgsg/pgsg_1/src

    # smoke test: 3 lambdas, 3 seeds, 60 epochs (~1 min)
    python scripts/02_lambda_sweep_controlled.py \
        --lambdas 0,0.2,1 --seeds 3 --epochs 60 --out results/ctl_piloto

    # full grid, both optimizers
    python scripts/02_lambda_sweep_controlled.py --optimizer adam  --out results/ctl_adam
    python scripts/02_lambda_sweep_controlled.py --optimizer adamw --out results/ctl_adamw
"""

from __future__ import annotations

import argparse
import csv as csvmod
import importlib.util
import itertools
import os
import sys
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from pgsg_3.m_model.pgsg_v3 import (  # noqa: E402
    PGSGv3Model,
    ensure_pgsg1_importable,
    kl_bernoulli_np,
)
from pgsg_3.g_ingest.grouped import (  # noqa: E402
    check_alignment,
    fruit_groups,
    group_split,
    pls_reference_relevance,
)

ensure_pgsg1_importable()

_EPS = 1e-12
SEP = "=" * 78
SEASON = 4
TEST_FRACTION = 0.2
# A gate is inert when the sigmoid derivative s(1-s) falls below this; the
# threshold is the one used in the saturation study of the programme.
INERT_THRESHOLD = 1e-3


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


# --------------------------------------------------------------- metrics
def r2(y_true, y_pred) -> float:
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def spearman(a, b) -> float:
    from scipy.stats import rankdata
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def entropia(g) -> float:
    gh = np.asarray(g, dtype=np.float64)
    gh = gh / max(gh.sum(), _EPS)
    gh = np.clip(gh, _EPS, None)
    return float(-(gh * np.log(gh)).sum())


def tv(g) -> float:
    """Total variation per band index.

    Comparable within one dataset only; cross-modality comparison requires
    normalisation per physical unit (cm^-1).
    """
    g = np.asarray(g, dtype=np.float64)
    return float(np.abs(np.diff(g)).mean()) if len(g) > 1 else 0.0


def hoyer(g) -> float:
    g = np.asarray(g, dtype=np.float64)
    p = len(g)
    l1 = np.abs(g).sum()
    l2 = np.sqrt((g ** 2).sum())
    if l2 < _EPS:
        return 0.0
    return float((np.sqrt(p) - l1 / l2) / (np.sqrt(p) - 1.0))


def n_inert(g) -> int:
    """Bands whose sigmoid derivative has collapsed: the data cannot reach them."""
    g = np.asarray(g, dtype=np.float64)
    return int((g * (1.0 - g) < INERT_THRESHOLD).sum())


def jaccard_medio(gates, decil: float = 0.10) -> float:
    if len(gates) < 2:
        return float("nan")
    q = int(np.ceil(decil * len(gates[0])))
    topos = [set(np.argsort(g)[::-1][:q].tolist()) for g in gates]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(topos, 2)]))


# ----------------------------------------------------------- prior arms
def permute_prior(prior: np.ndarray, mode: str, seed: int) -> np.ndarray:
    """Control arms for the prior, used to separate chemistry from anchoring.

    `literature` : the prior as published, unchanged.
    `blocks`     : the contiguous elevated regions are relocated to random
                   positions. Preserves the multiset of values, the number of
                   blocks, each block's length and internal shape -- destroys
                   only WHERE they sit. Tests whether contiguous emphasis
                   anywhere works as well as emphasis on the right bands.
    `shuffled`   : a full permutation. Destroys chemistry AND contiguity, so a
                   collapse here cannot distinguish the two; it is the weaker
                   control, reported alongside `blocks`.

    The permutation is drawn once per PARTITION (seed = split seed) and shared
    by every model seed, so that cross-seed Jaccard stays interpretable: with
    a different prior per run the gates would differ for a trivial reason.
    """
    prior = np.asarray(prior, dtype=float)
    if mode == "literature":
        return prior.copy()
    rng = np.random.default_rng(seed)
    if mode == "shuffled":
        return rng.permutation(prior)
    if mode != "blocks":
        raise ValueError(f"prior mode desconhecido: {mode!r}")

    base = prior.min()
    elevado = prior > base
    # runs maximais de bandas elevadas
    blocos, i, p = [], 0, len(prior)
    while i < p:
        if elevado[i]:
            j = i
            while j < p and elevado[j]:
                j += 1
            blocos.append(prior[i:j].copy())
            i = j
        else:
            i += 1

    novo = np.full(p, base)
    ocupado = np.zeros(p, dtype=bool)
    for b in sorted(blocos, key=len, reverse=True):   # maiores primeiro
        for _ in range(10_000):
            inicio = int(rng.integers(0, p - len(b) + 1))
            if not ocupado[inicio:inicio + len(b)].any():
                novo[inicio:inicio + len(b)] = b
                ocupado[inicio:inicio + len(b)] = True
                break
        else:
            raise SystemExit("nao foi possivel realocar os blocos sem sobreposicao")
    return novo


# ------------------------------------------------------------------ data
def carregar_modulo(path: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def achar_csv(root: Path):
    achados = []
    for pat in ("*angoDMC*.csv", "*mango*.csv", "*Mango*.csv", "*dmc*.csv"):
        achados.extend(root.rglob(pat))
    achados = [a for a in achados if ".git" not in a.parts]
    return max(achados, key=lambda p: p.stat().st_size) if achados else None


def preparar(pgsg1_root: Path, csv_path, split_seed: int, agrupado: bool):
    """Season 4, split (grouped by fruit), preprocessing fitted on train only."""
    mod = carregar_modulo(pgsg1_root / "run_experiment_v2.py", "run_exp_ctl")
    mmod = carregar_modulo(pgsg1_root / "pgsg_v2.py", "pgsg_v2_ctl")
    DS = mmod.SpectralDataset

    csv_path = csv_path or achar_csv(pgsg1_root)
    if csv_path is None:
        raise SystemExit(f"Mango CSV not found under {pgsg1_root}; use --csv")

    full = mod.load_mango_dmc_v3(csv_path)
    mask = np.asarray(full.group_ids) == SEASON
    X, y = np.asarray(full.X)[mask], np.asarray(full.y)[mask]
    wl = np.asarray(full.wavelengths)
    meta = dict(full.metadata)

    if agrupado:
        fruit = fruit_groups(csv_path, SEASON)
        check_alignment(fruit, y, csv_path, SEASON)
        tr, te = group_split(fruit, TEST_FRACTION, split_seed)
        n_fruits = int(len(np.unique(fruit)))
    else:
        from sklearn.model_selection import train_test_split
        tr, te = train_test_split(np.arange(len(y)), test_size=TEST_FRACTION,
                                  random_state=split_seed)
        fruit, n_fruits = None, None

    raw_tr = DS(X=X[tr], y=y[tr], wavelengths=wl, metadata=dict(meta))
    raw_te = DS(X=X[te], y=y[te], wavelengths=wl, metadata=dict(meta))
    prep = mod.Preprocessor(drop_zero_bands=True, apply_snv=True, normalize_target=False)
    X_tr, y_tr = prep.fit_transform(raw_tr)
    X_te, y_te = prep.transform(raw_te)
    wl_ef = np.asarray(prep.params.kept_wavelengths)

    ds_tr = DS(X=X_tr, y=y_tr, wavelengths=wl_ef, metadata=dict(meta))
    ds_te = DS(X=X_te, y=y_te, wavelengths=wl_ef, metadata=dict(meta))
    prior_lit = np.asarray(mod.make_literature_prior(wl_ef))
    groups_tr = fruit[tr] if fruit is not None else None
    return ds_tr, ds_te, np.asarray(y_te), prior_lit, wl_ef, groups_tr, n_fruits, csv_path


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg1-root", default=str(Path.home() / "Dropbox/pgsg/pgsg_1"))
    ap.add_argument("--csv", default=None)
    ap.add_argument("--lambdas", default="0,1e-3,1e-2,0.1,0.2,0.3,0.5,0.7,1,10")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--init", choices=["prior", "zero"], default="zero")
    ap.add_argument("--optimizer", choices=["adam", "adamw"], default="adam")
    ap.add_argument("--epochs", type=int, default=500,
                    help="fixed step budget; every run takes exactly this many")
    ap.add_argument("--split", choices=["grouped", "random"], default="grouped")
    ap.add_argument("--split-seed", type=int, default=42)
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--decil", type=float, default=0.10)
    ap.add_argument("--pls-h-max", type=int, default=120)
    ap.add_argument("--prior", choices=["literature", "blocks", "shuffled"],
                    default="literature",
                    help="braco de prior; 'blocks' e 'shuffled' sao controles "
                         "que separam conteudo quimico de ancoragem pura")
    ap.add_argument("--out", default="results/ctl_adam")
    a = ap.parse_args()

    lambdas = [float(x) for x in a.lambdas.split(",")]
    seeds = list(range(a.seeds))
    root = Path(os.path.expanduser(a.pgsg1_root))
    csv_arg = Path(os.path.expanduser(a.csv)) if a.csv else None

    head("Setup")
    (tr, te, y_te, prior_lit, wl, groups_tr,
     n_fruits, csv_path) = preparar(root, csv_arg, a.split_seed, a.split == "grouped")
    p = np.asarray(tr.X).shape[1]
    # a permutacao usa a semente da PARTICAO, fixa entre as sementes de modelo
    prior = permute_prior(prior_lit, a.prior, a.split_seed)
    print(f"csv       : {csv_path}")
    print(f"split     : {a.split}" + (f"  ({n_fruits} fruits)" if n_fruits else ""))
    print(f"train/test: {np.asarray(tr.X).shape} / {np.asarray(te.X).shape}   p={p}")
    print(f"init      : {a.init}   optimizer: {a.optimizer}   epochs: {a.epochs} (fixed)")
    print(f"prior arm : {a.prior}" + ("" if a.prior == "literature" else
          f"   (permutado com a semente da particao, {a.split_seed})"))
    print(f"lambdas   : {lambdas}")
    print(f"seeds     : {seeds}   ({len(lambdas) * len(seeds)} runs)")

    # --- non-circular relevance reference, from the training partition only
    ref = pls_reference_relevance(np.asarray(tr.X), np.asarray(tr.y), groups_tr,
                                  h_max=a.pls_h_max, seed=a.split_seed)
    relevance = ref["relevance"]
    from pgsg_3.g_ingest.grouped import fit_pls
    pls_pred = fit_pls(np.asarray(tr.X), np.asarray(tr.y), ref["h_1se"]).predict(
        np.asarray(te.X))
    pls_r2 = r2(y_te, pls_pred)
    print(f"\nPLS-1se   : H={ref['h_1se']} (cvmin H={ref['h_cvmin']}, "
          f"grid max {ref['h_max_effective']})   test R2={pls_r2:.4f}")
    print(f"prior ({a.prior}) vs PLS relevance : {spearman(prior, relevance):+.4f}")
    if a.prior != "literature":
        print(f"prior (literature) vs PLS relevance: "
              f"{spearman(prior_lit, relevance):+.4f}   <- teto do braco real")

    # ------------------------------------------------------------- run
    head("Running")
    linhas: list[dict] = []
    gates_por_lambda: dict[float, list[np.ndarray]] = {}
    t0 = time.time()

    for lam in lambdas:
        gates_por_lambda[lam] = []
        for seed in seeds:
            m = PGSGv3Model(
                lam=lam, init_from_prior=(a.init == "prior"),
                optimizer=a.optimizer, fixed_epochs=True,
                hidden=a.hidden, lr=a.lr, weight_decay=a.weight_decay,
                max_epochs=a.epochs, patience=a.epochs,
                batch_size=a.batch_size, seed=seed,
            )
            m.fit(tr, prior=prior)
            g = np.asarray(m.gates)
            gates_por_lambda[lam].append(g)
            linhas.append({
                "lam": lam, "seed": seed, "init": a.init, "prior_arm": a.prior,
                "optimizer": a.optimizer, "epochs": a.epochs, "split": a.split,
                "r2": r2(y_te, m.predict(te)),
                "rho_prior": float(np.corrcoef(g, prior)[0, 1]),
                "agree_pls": spearman(g, relevance),
                "kl": kl_bernoulli_np(g, prior),
                "entropia": entropia(g),
                "tv": tv(g),
                "hoyer": hoyer(g),
                "n_inert": n_inert(g),
                "best_epoch": int(m.train_history["best_epoch"]),
            })
            r = linhas[-1]
            print(f"  lam={lam:<8g} seed={seed:<2}  R2={r['r2']:.4f}  "
                  f"rho={r['rho_prior']:.4f}  agree={r['agree_pls']:+.4f}  "
                  f"inert={r['n_inert']:<3}")

    print(f"\nelapsed: {time.time() - t0:.0f}s")

    # --------------------------------------------------------- write out
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "runs.csv").open("w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    agreg = []
    for lam in lambdas:
        sub = [r for r in linhas if r["lam"] == lam]
        reg = {"lam": lam, "init": a.init, "prior_arm": a.prior, "optimizer": a.optimizer,
               "epochs": a.epochs, "split": a.split, "k": len(sub)}
        for c in ("r2", "rho_prior", "agree_pls", "kl", "entropia",
                  "tv", "hoyer", "n_inert"):
            v = np.asarray([r[c] for r in sub], dtype=float)
            reg[f"{c}_mean"] = v.mean()
            reg[f"{c}_sd"] = v.std(ddof=1) if len(v) > 1 else 0.0
        reg["jaccard"] = jaccard_medio(gates_por_lambda[lam], a.decil)
        agreg.append(reg)

    with (out / "aggregate.csv").open("w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=list(agreg[0].keys()))
        w.writeheader()
        w.writerows(agreg)

    np.savez_compressed(
        out / "gates.npz",
        prior=prior, prior_literature=prior_lit, prior_arm=a.prior,
        wavelengths=wl, pls_relevance=relevance,
        pls_h_1se=ref["h_1se"], pls_r2=pls_r2,
        lambdas=np.asarray(lambdas), seeds=np.asarray(seeds),
        **{f"gates_lam{lam:g}": np.stack(gates_por_lambda[lam]) for lam in lambdas},
    )
    print(f"written: {out}/runs.csv, aggregate.csv, gates.npz")

    # ------------------------------------------------------------ report
    head("Regularization path")
    print(f"{'lam':>8} {'R2':>16} {'rho(g,s)':>16} {'agree PLS':>16} "
          f"{'Jaccard':>8} {'inert':>6} {'Hoyer':>7}")
    for r in agreg:
        print(f"{r['lam']:>8g} {r['r2_mean']:>9.4f}±{r['r2_sd']:.4f} "
              f"{r['rho_prior_mean']:>9.4f}±{r['rho_prior_sd']:.4f} "
              f"{r['agree_pls_mean']:>+9.4f}±{r['agree_pls_sd']:.4f} "
              f"{r['jaccard']:>8.4f} {r['n_inert_mean']:>6.1f} {r['hoyer_mean']:>7.4f}")
    print(f"\nreference: calibrated PLS-1se test R2 = {pls_r2:.4f}  "
          f"(gate model best = {max(r['r2_mean'] for r in agreg):.4f})")

    # H0, by the criterion fixed before any run
    head("H0 (pre-registered criterion)")
    r2_max = max(r["r2_mean"] for r in agreg)
    r2_sd_ref = max(r["r2_sd"] for r in agreg)
    cand = [r for r in agreg
            if r["rho_prior_mean"] < 0.95
            and r["r2_mean"] >= r2_max - r2_sd_ref
            and r["jaccard"] >= 0.90]
    print(f"rho < 0.95  AND  R2 >= {r2_max - r2_sd_ref:.4f}  AND  Jaccard >= 0.90")
    if cand:
        print("SUPPORTED at:")
        for r in cand:
            print(f"  lam={r['lam']:g}  R2={r['r2_mean']:.4f}  "
                  f"rho={r['rho_prior_mean']:.4f}  J={r['jaccard']:.4f}")
    else:
        print("NOT supported on this grid. See outcomes (b) and (c) in "
              "docs/protocolo_hipoteses.md.")

    # Exploratory axis, declared as such
    head("Agreement with the PLS reference (EXPLORATORY, added Oct 2026)")
    best = max(agreg, key=lambda r: r["agree_pls_mean"])
    print(f"prior alone        : {spearman(prior, relevance):+.4f}")
    for r in agreg:
        mark = "   <-- max" if r is best else ""
        print(f"  lam={r['lam']:<8g} {r['agree_pls_mean']:+.4f} "
              f"± {r['agree_pls_sd']:.4f}{mark}")
    ends = (agreg[0]["agree_pls_mean"], agreg[-1]["agree_pls_mean"])
    if best is not agreg[0] and best is not agreg[-1]:
        print(f"\nInterior maximum at lam={best['lam']:g}: the gate agrees with the "
              "data-derived\nreference better than either extreme. Anchoring buys "
              "something the data alone\ndo not supply, and full anchoring gives it back.")
    else:
        print(f"\nMonotone across the grid (ends {ends[0]:+.4f} -> {ends[1]:+.4f}): "
              "no interior\noptimum, so on these data the prior is worth either all "
              "or nothing.")


if __name__ == "__main__":
    main()
