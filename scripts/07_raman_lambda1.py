#!/usr/bin/env python
"""Raman control arm: are the NIR metric defects absent with a continuous prior?

Implements, verbatim, the criteria fixed in `docs/pre-registro-H12-raman.md`,
committed with this script before any Raman execution.

The NIR prior is a four-level step function with a 34-band plateau against a
decile of 28--29, and findings F002/F003/F004 traced three defects to that
quantisation. The Raman prior is continuous (sum of 19 gaussians, 545 distinct
values, plateau of one band at the maximum, 1326 bands tied at the 0.01 floor).
If the explanation is right, the three defects must be absent here.

WHAT IS FIXED AND NOT EXPOSED
-----------------------------
lambda is {0, 1}. It is a module constant, deliberately NOT a command-line
flag, so the grid cannot drift during execution. Same for the three thresholds.

USAGE
-----
    # validate the chain first; writes nothing, reports nothing usable
    python scripts/07_raman_lambda1.py --quick \
        --pgsg1-root ~/Dropbox/pgsg/pgsg_1 \
        --pgsg2-root ~/pgsg/pgsg2-nir-raman-gating/src

    # the registered run
    python scripts/07_raman_lambda1.py \
        --pgsg1-root ~/Dropbox/pgsg/pgsg_1 \
        --pgsg2-root ~/pgsg/pgsg2-nir-raman-gating/src \
        --out results/raman_h12
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

SEP = "=" * 78

# ----------------------------------------- fixed by the pre-registration
LAMBDAS = (0.0, 1.0)
PARTICOES = (0, 1, 2)
N_SEEDS = 10
DECIL = 0.10
TEST_FRACTION = 0.2
EPOCAS = 500
HIDDEN = 32
ALPHA = 0.05
PLS_H_MAX = 120
LIM_H12A = 0.5      # decile fraction inside the prior's largest tie group
LIM_H12B = 0.02     # max |J(index) - J(random ties)| for "no collapse"
SORTEIOS = 200      # tie-break draws
# -----------------------------------------------------------------------

AMOSTRAS_QUICK, BANDAS_QUICK, EPOCAS_QUICK = 300, 200, 30


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}", flush=True)


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def topo(v: np.ndarray, q: int) -> np.ndarray:
    return np.argsort(v)[::-1][:q]


def jaccard_indice(gates: list[np.ndarray], q: int) -> float:
    """Exactly the published computation: argsort, ties as the sort leaves."""
    tops = [set(topo(g, q).tolist()) for g in gates]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


def jaccard_sorteado(gates: list[np.ndarray], q: int, draws: int = SORTEIOS,
                     seed: int = 0) -> tuple[float, float]:
    """Same, with exact ties broken at random. lexsort's last key decides only
    among equal gate values and never reorders distinct ones."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        tops = []
        for g in gates:
            chave = rng.random(len(g))
            tops.append(set(np.lexsort((chave, -g))[:q].tolist()))
        vals.append(np.mean([len(a & b) / len(a | b)
                             for a, b in itertools.combinations(tops, 2)]))
    v = np.asarray(vals)
    return float(v.mean()), float(v.std(ddof=1) if len(v) > 1 else 0.0)


def maior_grupo_empate(prior: np.ndarray) -> np.ndarray:
    """Band indices of the prior's largest group of exactly equal values.

    In NIR that is the 223-band floor, and the decile sits in the 34-band
    plateau instead. In Raman it is the 1326-band floor at 0.01. H12a asks
    whether the decile is pinned inside it."""
    valores, contagens = np.unique(prior, return_counts=True)
    maior = valores[int(np.argmax(contagens))]
    return np.flatnonzero(prior == maior)


def empates_exatos(g: np.ndarray) -> int:
    return int(len(g) - len(np.unique(g)))


# --------------------------------------------------------------------- loading

def importar(pgsg1_root: Path, pgsg2_root: Path):
    """pgsg_2's Raman modules use absolute package imports, so the package
    root goes on sys.path -- the same mechanism 02 uses for PGSG1_ROOT."""
    for p in (str(pgsg2_root.resolve()), str(pgsg1_root.resolve()),
              str((pgsg1_root / "src").resolve())):
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        from pgsg2.ingestion.raman_bioprocess import (
            RamanBioprocessSubstratesLoader)
        from pgsg2.models.adapter import to_pgsg1_dataset
        from pgsg2.preprocessing.raman import RamanPreprocessor
        from pgsg2.priors.raman import RamanGlucosePrior
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"could not import the pgsg_2 Raman modules ({e}).\n"
            f"--pgsg2-root must be the directory that CONTAINS the `pgsg2` "
            f"package, i.e. the repository's `src`:\n"
            f"    --pgsg2-root ~/pgsg/pgsg2-nir-raman-gating/src\n"
            f"given: {pgsg2_root.resolve()}") from None
    try:
        from pgsg_1.ingestion import SpectralDataset
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"could not import pgsg_1 ({e}).\n"
            f"--pgsg1-root must be the pgsg_1 repository root (the directory "
            f"holding `src/pgsg_1` and `pgsg_v2.py`):\n"
            f"    --pgsg1-root ~/Dropbox/pgsg/pgsg_1\n"
            f"given: {pgsg1_root.resolve()}") from None

    return dict(Loader=RamanBioprocessSubstratesLoader,
                Prep=RamanPreprocessor, Prior=RamanGlucosePrior,
                to_pgsg1=to_pgsg1_dataset, DS=SpectralDataset)


def carregar_modulo(path: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def subamostrar(ds, DS, n_amostras: int, n_bandas: int, seed: int):
    rng = np.random.default_rng(seed)
    ia = rng.choice(ds.n_samples, size=min(n_amostras, ds.n_samples),
                    replace=False)
    ia.sort()
    ib = np.unique(np.linspace(0, ds.n_bands - 1,
                               min(n_bandas, ds.n_bands)).round().astype(int))
    return DS(X=ds.X[np.ix_(ia, ib)], y=ds.y[ia],
              wavelengths=ds.wavelengths[ib], metadata=dict(ds.metadata))


def dividir(ds, DS, seed: int):
    from sklearn.model_selection import train_test_split
    tr, te = train_test_split(np.arange(ds.n_samples),
                              test_size=TEST_FRACTION, random_state=seed)
    mk = lambda i: DS(X=ds.X[i], y=ds.y[i], wavelengths=ds.wavelengths,
                      metadata=dict(ds.metadata))
    return mk(tr), mk(te)


# ------------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg1-root", required=True)
    ap.add_argument("--pgsg2-root", required=True,
                    help="the pgsg_2 'src' directory, which holds the pgsg2 "
                         "package")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.quick and a.out:
        raise SystemExit("--quick never writes results; drop --out.")
    if not a.quick and not a.out:
        raise SystemExit("the registered run needs --out.")

    raiz3 = Path(__file__).resolve().parents[1]
    pgsg1 = Path(a.pgsg1_root).expanduser()
    pgsg2 = Path(a.pgsg2_root).expanduser()

    mods = importar(pgsg1, pgsg2)
    DS = mods["DS"]
    sweep = carregar_modulo(raiz3 / "scripts" / "02_lambda_sweep_controlled.py",
                            "sweep02")
    permute_prior = sweep.permute_prior          # same tested function as NIR
    sys.path.insert(0, str(raiz3 / "src"))
    from pgsg_3.g_ingest.grouped import pls_reference_relevance
    from pgsg_3.m_model.pgsg_v3 import PGSGv3Model

    if a.quick:
        print("#" * 78)
        print("#  QUICK MODE: subsampled and shortened. It checks that the")
        print("#  chain loads, preprocesses, builds the prior and trains.")
        print("#  The numbers it prints are NOT results and go nowhere.")
        print("#" * 78, flush=True)

    t0 = time.time()
    log = lambda m: print(f"[{time.time() - t0:7.1f}s] {m}", flush=True)

    head("Loading")
    ds2 = mods["Loader"]().load()
    log(f"loaded: n={ds2.n_samples}, p={ds2.n_bands}")
    ds2 = mods["Prep"]().fit_transform(ds2)
    log("preprocessed (cosmic rays, ALS baseline, SNV)")
    ds = mods["to_pgsg1"](ds2, target_unit="unknown")
    if a.quick:
        ds = subamostrar(ds, DS, AMOSTRAS_QUICK, BANDAS_QUICK, 0)
        log(f"quick subsample: n={ds.n_samples}, p={ds.n_bands}")

    epocas = EPOCAS_QUICK if a.quick else EPOCAS
    particoes = (0,) if a.quick else PARTICOES
    seeds = list(range(2 if a.quick else N_SEEDS))

    p = int(ds.n_bands)
    q = max(1, p // 10)        # the published definition, as in NIR
    head("Setup")
    print(f"bands p        : {p}")
    print(f"top-q (p // 10): {q}")
    print(f"lambdas        : {list(LAMBDAS)}   (fixed, not a flag)")
    print(f"partitions     : {list(particoes)}   seeds: {len(seeds)}")
    print(f"epochs         : {epocas} (fixed)   init: zero   optimizer: adam")

    linhas, celulas = [], {}
    for sseed in particoes:
        tr, te = dividir(ds, DS, sseed)
        prior_lit = np.asarray(mods["Prior"]().compute(tr.wavelengths), float)
        niveis = len(np.unique(prior_lit))
        grupo = maior_grupo_empate(prior_lit)
        plato = np.flatnonzero(prior_lit >= prior_lit.max() - 1e-9)
        log(f"partition {sseed}: train n={tr.n_samples}, test n={te.n_samples}; "
            f"prior has {niveis} distinct values, plateau {len(plato)}, "
            f"largest tie group {len(grupo)}")

        log(f"partition {sseed}: calibrating the PLS reference (H_MAX="
            f"{PLS_H_MAX}, 5 plain folds -- no group ids exist)")
        ref = pls_reference_relevance(np.asarray(tr.X), np.asarray(tr.y),
                                      None, h_max=PLS_H_MAX, n_folds=5,
                                      seed=42)
        relevance = np.abs(np.asarray(ref["relevance"], float))
        log(f"partition {sseed}: PLS H(1se)={ref['h_1se']} "
            f"(cvmin {ref['h_cvmin']}, grid max {ref['h_max_effective']})")
        if ref["at_boundary"]:
            log(f"partition {sseed}: WARNING the CV minimum sits at the grid "
                f"boundary, so H_MAX={PLS_H_MAX} may be too small for p={p}. "
                f"Recorded, not changed: the grid is fixed by the "
                f"pre-registration.")

        for arm in ("literature", "blocks", "shuffled"):
            prior = (prior_lit if arm == "literature"
                     else np.asarray(permute_prior(prior_lit, arm, sseed),
                                     float))
            for lam in LAMBDAS:
                gates = []
                for seed in seeds:
                    m = PGSGv3Model(lam=lam, init_from_prior=False,
                                    optimizer="adam", fixed_epochs=True,
                                    hidden=HIDDEN, max_epochs=epocas,
                                    patience=epocas, seed=seed)
                    m.fit(tr, prior=prior)
                    g = np.asarray(m.gates, float)
                    gates.append(g)
                    linhas.append({
                        "particao": sseed, "arm": arm, "lam": lam,
                        "seed": seed,
                        "agree": spearman(g, relevance),
                        "rho_prior": float(np.corrcoef(g, prior)[0, 1]),
                        "empates": empates_exatos(g),
                    })
                ji = jaccard_indice(gates, q)
                jr, jsd = jaccard_sorteado(gates, q)
                dentro_grupo = float(np.mean(
                    [len(set(topo(g, q).tolist()) & set(grupo.tolist())) / q
                     for g in gates]))
                dentro_plato = float(np.mean(
                    [len(set(topo(g, q).tolist()) & set(plato.tolist())) / q
                     for g in gates]))
                celulas[(sseed, arm, lam)] = {
                    "j_index": ji, "j_random": jr, "j_random_sd": jsd,
                    "delta_j": ji - jr, "in_tie_group": dentro_grupo,
                    "in_plateau": dentro_plato,
                    "agree": float(np.mean([r["agree"] for r in linhas
                                            if r["particao"] == sseed
                                            and r["arm"] == arm
                                            and r["lam"] == lam])),
                    "max_empates": max(empates_exatos(g) for g in gates),
                    "prior_rho_ref": spearman(prior, relevance),
                    "niveis": niveis, "plato": len(plato),
                    "grupo": len(grupo), "pls_h": int(ref["h_1se"]),
                    "pls_h_cvmin": int(ref["h_cvmin"]),
                    "pls_at_boundary": bool(ref["at_boundary"]),
                }
                log(f"  {arm:<11} lam={lam:<4g} J={ji:.4f} "
                    f"Jrnd={jr:.4f} in_group={dentro_grupo:.3f} "
                    f"agree={celulas[(sseed, arm, lam)]['agree']:+.4f}")

    if a.quick:
        head("Quick mode finished")
        print("The chain works. Nothing above is a result. Re-run without")
        print("--quick and with --out for the registered execution.")
        return

    # ------------------------------------------------------------- write out
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    import csv as csvmod
    with (out / "runs.csv").open("w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    with (out / "cells.json").open("w") as f:
        json.dump({f"{k[0]}|{k[1]}|{k[2]:g}": v for k, v in celulas.items()},
                  f, indent=1)
    log(f"written: {out}/runs.csv, cells.json")

    # ------------------------------------------------------------- verdicts
    head("H12a - the decile is not pinned inside a tie group (lam=1)")
    print(f"Fraction of the top-{q} inside the prior's largest group of equal")
    print(f"values. H12a needs it below {LIM_H12A}. In NIR the decile sits")
    print("1.000 inside the plateau in 15/15 cells.\n")
    print(f"  {'partition':<10} {'tie group':>10} {'in group':>9} "
          f"{'in plateau':>11}   H12a")
    k_a = 0
    for s in particoes:
        c = celulas[(s, "literature", 1.0)]
        ok = c["in_tie_group"] < LIM_H12A
        k_a += ok
        print(f"  {s:<10} {c['grupo']:>10} {c['in_tie_group']:>9.3f} "
              f"{c['in_plateau']:>11.3f}   {'ok' if ok else '-'}")

    head("H12b - no collapse when ties are broken at random (lam=1)")
    print(f"H12b needs |J(index) - J(random)| < {LIM_H12B}. In NIR the gap is")
    print("+0.2413 for the accepted paper's arm and of the same order in all")
    print("seven pgsg_1 R2 cells.\n")
    print(f"  {'partition':<10} {'exact ties':>11} {'J index':>9} "
          f"{'J random':>9} {'gap':>8}   H12b")
    k_b = 0
    for s in particoes:
        c = celulas[(s, "literature", 1.0)]
        ok = abs(c["delta_j"]) < LIM_H12B
        k_b += ok
        print(f"  {s:<10} {c['max_empates']:>11} {c['j_index']:>9.4f} "
              f"{c['j_random']:>9.4f} {c['delta_j']:>+8.4f}   "
              f"{'ok' if ok else '-'}")

    head("H12c - literature beats blocks on whole-spectrum agreement (lam=1)")
    print("Paired by seed, two-sided Wilcoxon. In NIR blocks equals or beats")
    print("literature in 10/10 partitions.\n")
    print(f"  {'partition':<10} {'lit':>9} {'blocks':>9} {'delta':>9} "
          f"{'p':>8}   H12c")
    k_c = 0
    for s in particoes:
        al = np.array([r["agree"] for r in linhas if r["particao"] == s
                       and r["arm"] == "literature" and r["lam"] == 1.0])
        ab = np.array([r["agree"] for r in linhas if r["particao"] == s
                       and r["arm"] == "blocks" and r["lam"] == 1.0])
        d = al - ab
        pv = 1.0 if np.allclose(d, 0) else float(wilcoxon(d).pvalue)
        ok = bool(d.mean() > 0 and pv < ALPHA)
        k_c += ok
        print(f"  {s:<10} {al.mean():>+9.4f} {ab.mean():>+9.4f} "
              f"{d.mean():>+9.4f} {pv:>8.4f}   {'ok' if ok else '-'}")

    head("Reported alongside, no verdict")
    print(f"  {'partition':<10} {'arm':<11} {'rho(prior,ref)':>15} "
          f"{'J lam=0':>9} {'J lam=1':>9} {'agree lam=0':>12}")
    for s in particoes:
        for arm in ("literature", "blocks", "shuffled"):
            c0, c1 = celulas[(s, arm, 0.0)], celulas[(s, arm, 1.0)]
            print(f"  {s:<10} {arm:<11} {c1['prior_rho_ref']:>+15.4f} "
                  f"{c0['j_index']:>9.4f} {c1['j_index']:>9.4f} "
                  f"{c0['agree']:>+12.4f}")

    n = len(particoes)
    head("Pre-registered verdicts")
    for nome, k, limiar, crit in (
            ("H12a", k_a, n, f"decile fraction in largest tie group < {LIM_H12A}"),
            ("H12b", k_b, n, f"|J(index) - J(random)| < {LIM_H12B}"),
            ("H12c", k_c, 2, f"literature > blocks, paired Wilcoxon p < {ALPHA}")):
        print(f"{nome:<6} {k}/{n} partitions (need {limiar})  "
              f"-> {'SUPPORTED' if k >= limiar else 'NOT SUPPORTED'}")
        print(f"{'':6} criterion: {crit}")
        print()

    head("Reading")
    if k_a >= n and k_b >= n:
        print("H12a and H12b supported: with a continuous prior the decile is")
        print("not pinned inside a tie group and the Jaccard does not depend on")
        print("tie order. The two defects of findings F002 and F004 are absent,")
        print("which is what the quantisation explanation predicts.")
    else:
        print("H12a or H12b not supported: the defects are NOT specific to the")
        print("quantised prior, and the explanation in F002/F003/F004 has to be")
        print("widened. Report this as the outcome; do not look for a third")
        print("prior shape on these data.")
    print()
    if k_c >= 2:
        print("H12c supported: with a continuous prior, where the metric is not")
        print("dominated by between-level separation, the literature position")
        print("DOES beat a relocated one. That is the content signal the NIR")
        print("metric could not see.")
    else:
        print("H12c not supported: blocks equals or beats literature in Raman")
        print("too, so whole-spectrum insensitivity is not a quantisation")
        print("effect. Explanation (b) of H7 gains independent confirmation in")
        print("a second modality, which is a stronger result than H12c would")
        print("have been.")
    print()
    print("Not claimed here: any accuracy result. The Raman ingestion exposes")
    print("no batch or replicate id, the split is ungrouped, and replicate")
    print("leakage is undefended -- the very error pgsg_1's R2 corrected in")
    print("NIR. R2 is not reported for that reason.")


if __name__ == "__main__":
    main()
