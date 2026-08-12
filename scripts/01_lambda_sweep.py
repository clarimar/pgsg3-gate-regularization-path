#!/usr/bin/env python
"""Varredura do caminho de regularização em λ — experimento central do pgsg_3.

PROTOCOLO
---------
Segue `docs/protocolo_hipoteses.md`. Para cada λ da grade e cada semente:
treina a `PGSGv3Model`, mede desempenho e topologia do gate. Todos os
demais hiperparâmetros ficam fixos nos valores de pgsg_1, de modo que λ
seja a única variável.

MÉTRICAS
--------
Por execução (λ, semente):
  R²           desempenho no conjunto de teste fixo
  ρ_pearson    correlação gate-prior (definição de pgsg_1 §4.4 H3)
  ρ_spearman   idem, por postos (robusta a monotonia não linear)
  kl           KL_Bernoulli(gate ‖ prior), a quantidade penalizada
  entropia     H(ĝ) sobre o gate normalizado (pgsg_2 Eq. 1)
  tv           variação total por banda (pgsg_2 Eq. 2)
  hoyer        índice de esparsidade (pgsg_2 Eq. 3)
  best_epoch   época de melhor val_loss

Agregado por λ (entre as sementes):
  jaccard      sobreposição média do decil superior entre TODOS os pares

O Jaccard é a métrica que distingue H0 de uma pergunta já respondida:
sabe-se que existe solução com ρ baixo e R² equivalente (a condição não
informada de pgsg_1), mas com Jaccard ≤ 0,57. A questão é se λ permite
descolamento COM estabilidade.

USO
---
    export PGSG1_ROOT=~/Dropbox/pgsg/pgsg_1/src

    # piloto rápido, para validar o pipeline antes da grade cheia
    python scripts/01_lambda_sweep.py --lambdas 0,0.01,1 --seeds 3 \
        --n-train 400 --out results/sweep_piloto

    # grade do protocolo
    python scripts/01_lambda_sweep.py --out results/sweep_nir
"""

from __future__ import annotations

import argparse
import csv
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

ensure_pgsg1_importable()

_EPS = 1e-12
SEP = "=" * 74


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


# --------------------------------------------------------------- métricas
def r2(y_true, y_pred) -> float:
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def entropia(g: np.ndarray) -> float:
    """H(ĝ) sobre o gate normalizado (pgsg_2 Eq. 1).

    O gate é sigmoide independente, logo Σgᵢ ≠ 1; a normalização é
    necessária para que a entropia seja definida.
    """
    gh = np.asarray(g, dtype=np.float64)
    gh = gh / max(gh.sum(), _EPS)
    gh = np.clip(gh, _EPS, None)
    return float(-(gh * np.log(gh)).sum())


def tv(g: np.ndarray) -> float:
    """Variação total por banda (pgsg_2 Eq. 2).

    ATENÇÃO: comparações entre modalidades exigem normalizar por cm⁻¹ por
    banda; este valor é por ÍNDICE e só é comparável dentro de um mesmo
    dataset. Lição de pgsg_2 H3.
    """
    g = np.asarray(g, dtype=np.float64)
    return float(np.abs(np.diff(g)).mean()) if len(g) > 1 else 0.0


def hoyer(g: np.ndarray) -> float:
    """Índice de esparsidade de Hoyer (pgsg_2 Eq. 3), em [0, 1]."""
    g = np.asarray(g, dtype=np.float64)
    p = len(g)
    l1 = np.abs(g).sum()
    l2 = np.sqrt((g ** 2).sum())
    if l2 < _EPS:
        return 0.0
    return float((np.sqrt(p) - l1 / l2) / (np.sqrt(p) - 1.0))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    from scipy.stats import rankdata
    ra, rb = rankdata(a), rankdata(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def jaccard_medio(gates: list[np.ndarray], decil: float = 0.10) -> float:
    """Sobreposição média do decil superior entre TODOS os pares."""
    if len(gates) < 2:
        return float("nan")
    q = int(np.ceil(decil * len(gates[0])))
    topos = [set(np.argsort(g)[::-1][:q].tolist()) for g in gates]
    pares = [len(a & b) / len(a | b) for a, b in itertools.combinations(topos, 2)]
    return float(np.mean(pares))


# ----------------------------------------------------------------- dados
def carregar_modulo(path: Path, nome: str):
    import importlib.util
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


def preparar_nir(pgsg1_root: Path, csv_path: Path | None, season: int, n_train: int):
    """Reproduz o protocolo de pgsg_1: safra 4, split fixo, Preprocessor."""
    mod = carregar_modulo(pgsg1_root / "run_experiment_v2.py", "run_exp_sweep")
    mmod = carregar_modulo(pgsg1_root / "pgsg_v2.py", "pgsg_v2_sweep")
    SpectralDataset = mmod.SpectralDataset

    csv_path = csv_path or achar_csv(pgsg1_root)
    if csv_path is None:
        raise SystemExit(f"CSV do Mango não encontrado sob {pgsg1_root}; use --csv")

    ds_full = mod.load_mango_dmc_v3(csv_path)
    mask = np.asarray(ds_full.group_ids) == season
    ds4 = SpectralDataset(
        X=np.asarray(ds_full.X)[mask], y=np.asarray(ds_full.y)[mask],
        wavelengths=np.asarray(ds_full.wavelengths),
        metadata=dict(ds_full.metadata),
        group_ids=np.asarray(ds_full.group_ids)[mask],
    )
    gen = mod.ScenarioGenerator(
        test_strategy=mod.FixedFractionTest(fraction=0.2, seed=42),
        train_strategy=mod.StratifiedTrainSampler(),
        n_grid=[n_train], seeds=[0],
    )
    gen.fit(ds4)
    sc = next(iter(gen.iter_scenarios()))

    prep = mod.Preprocessor(drop_zero_bands=True, apply_snv=True, normalize_target=False)
    X_tr, y_tr = prep.fit_transform(sc.train_dataset)
    X_te, y_te = prep.transform(sc.test_dataset)
    wl = np.asarray(prep.params.kept_wavelengths)
    meta = dict(sc.train_dataset.metadata)

    tr = SpectralDataset(X=X_tr, y=y_tr, wavelengths=wl, metadata=dict(meta))
    te = SpectralDataset(X=X_te, y=y_te, wavelengths=wl, metadata=dict(meta))
    prior = np.asarray(mod.make_literature_prior(wl))
    return tr, te, np.asarray(y_te), prior, wl


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg1-root", default=os.environ.get("PGSG1_ROOT_REPO",
                    str(Path.home() / "Dropbox/pgsg/pgsg_1")))
    ap.add_argument("--csv", default=None)
    ap.add_argument("--season", type=int, default=4)
    ap.add_argument("--n-train", type=int, default=1159)
    ap.add_argument("--lambdas", default="0,1e-4,1e-3,1e-2,1e-1,1,10")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--max-epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--decil", type=float, default=0.10)
    ap.add_argument("--init", choices=["prior", "zero"], default="prior",
                    help="'prior': theta0=logit(s) (varredura 1, lambda inerte). "
                         "'zero': theta0=0, prior so como referencia da penalidade "
                         "(varredura 2, caminho informativo)")
    ap.add_argument("--out", default="results/sweep_nir")
    a = ap.parse_args()

    lambdas = [float(x) for x in a.lambdas.split(",")]
    seeds = list(range(a.seeds))
    pgsg1_root = Path(os.path.expanduser(a.pgsg1_root))

    head("Setup")
    tr, te, y_te, prior, wl = preparar_nir(
        pgsg1_root, Path(os.path.expanduser(a.csv)) if a.csv else None,
        a.season, a.n_train)
    p = np.asarray(tr.X).shape[1]
    print(f"treino={np.asarray(tr.X).shape}  teste={np.asarray(te.X).shape}  p={p}")
    print(f"init: {a.init}  "
          f"({'theta0=logit(s)' if a.init=='prior' else 'theta0=0, prior so na penalidade'})")
    print(f"λ  : {lambdas}")
    print(f"sementes: {seeds}   ({len(lambdas)*len(seeds)} execuções)")
    print(f"fixos: hidden={a.hidden} lr={a.lr} wd={a.weight_decay} "
          f"epochs={a.max_epochs} patience={a.patience} batch={a.batch_size}")

    head("Executando")
    linhas: list[dict] = []
    gates_por_lambda: dict[float, list[np.ndarray]] = {}
    t0 = time.time()

    for lam in lambdas:
        gates_por_lambda[lam] = []
        for seed in seeds:
            m = PGSGv3Model(
                lam=lam, init_from_prior=(a.init == "prior"),
                hidden=a.hidden, lr=a.lr, weight_decay=a.weight_decay,
                max_epochs=a.max_epochs, patience=a.patience,
                batch_size=a.batch_size, seed=seed,
            )
            m.fit(tr, prior=prior)
            g = np.asarray(m.gates)
            gates_por_lambda[lam].append(g)
            pred = m.predict(te)
            linhas.append({
                "lam": lam, "seed": seed, "init": a.init,
                "r2": r2(y_te, pred),
                "rho_pearson": float(np.corrcoef(g, prior)[0, 1]),
                "rho_spearman": spearman(g, prior),
                "kl": kl_bernoulli_np(g, prior),
                "entropia": entropia(g),
                "tv": tv(g),
                "hoyer": hoyer(g),
                "best_epoch": int(m.train_history["best_epoch"]),
            })
            r = linhas[-1]
            print(f"  λ={lam:<8g} seed={seed:<2}  R²={r['r2']:.4f}  "
                  f"ρ={r['rho_pearson']:.4f}  KL={r['kl']:.3e}  "
                  f"ep={r['best_epoch']}")

    print(f"\ntempo total: {time.time()-t0:.0f}s")

    # --------------------------------------------------------- gravação
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    campos = list(linhas[0].keys())
    with (out / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader(); w.writerows(linhas)

    agreg = []
    for lam in lambdas:
        sub = [r for r in linhas if r["lam"] == lam]
        reg = {"lam": lam, "init": a.init, "k": len(sub)}
        for c in ("r2", "rho_pearson", "rho_spearman", "kl", "entropia",
                  "tv", "hoyer", "best_epoch"):
            v = np.asarray([r[c] for r in sub], dtype=float)
            reg[f"{c}_media"] = v.mean()
            reg[f"{c}_sd"] = v.std(ddof=1) if len(v) > 1 else 0.0
        reg["jaccard"] = jaccard_medio(gates_por_lambda[lam], a.decil)
        agreg.append(reg)

    with (out / "agregado.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(agreg[0].keys()))
        w.writeheader(); w.writerows(agreg)

    np.savez_compressed(
        out / "gates.npz",
        prior=prior, wavelengths=wl,
        lambdas=np.asarray(lambdas), seeds=np.asarray(seeds),
        **{f"gates_lam{lam:g}": np.stack(gates_por_lambda[lam]) for lam in lambdas},
    )
    print(f"gravado: {out}/runs.csv, agregado.csv, gates.npz")

    # ---------------------------------------------------- leitura de H0
    head("Caminho de regularização")
    print(f"{'λ':>10} {'R²':>16} {'ρ(g,s)':>16} {'Jaccard':>8} {'KL':>10} {'Hoyer':>7}")
    for r in agreg:
        print(f"{r['lam']:>10g} {r['r2_media']:>9.4f}±{r['r2_sd']:.4f} "
              f"{r['rho_pearson_media']:>9.4f}±{r['rho_pearson_sd']:.4f} "
              f"{r['jaccard']:>8.4f} {r['kl_media']:>10.2e} "
              f"{r['hoyer_media']:>7.4f}")

    head("H0 — descolamento COM estabilidade")
    r2_max = max(r["r2_media"] for r in agreg)
    r2_sd_ref = max(r["r2_sd"] for r in agreg)
    cand = [r for r in agreg
            if r["rho_pearson_media"] < 0.95
            and r["r2_media"] >= r2_max - r2_sd_ref
            and r["jaccard"] >= 0.90]
    print(f"critério: ρ < 0,95  E  R² ≥ {r2_max - r2_sd_ref:.4f}  E  Jaccard ≥ 0,90")
    if cand:
        print("H0 SUPORTADA nos seguintes λ:")
        for r in cand:
            print(f"  λ={r['lam']:g}  R²={r['r2_media']:.4f}  "
                  f"ρ={r['rho_pearson_media']:.4f}  J={r['jaccard']:.4f}")
    else:
        print("H0 NÃO suportada nesta grade — nenhum λ satisfaz as três condições.")
        print("Ver desfechos (b) e (c) em docs/protocolo_hipoteses.md: transição")
        print("abrupta ou diagrama degenerado. Ambos são resultado, não falha.")
        if a.init == "prior":
            print("\nNOTA: com --init prior o gate já parte de s e a penalidade é")
            print("redundante com a inicialização. Para o caminho informativo,")
            print("repetir com --init zero.")
        rho_min = min(r["rho_pearson_media"] for r in agreg)
        print(f"\nmenor ρ observado: {rho_min:.4f} "
              f"(λ={[r['lam'] for r in agreg if r['rho_pearson_media']==rho_min][0]:g})")


if __name__ == "__main__":
    main()
