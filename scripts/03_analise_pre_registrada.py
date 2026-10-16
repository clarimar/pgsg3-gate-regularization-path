#!/usr/bin/env python
"""Pre-registered analysis of H5 and H6 across partitions.

This script implements, verbatim, the criteria fixed in
`docs/pre-registro-H5-H6.md` BEFORE any partition other than split_seed=42 was
run. It is committed together with that document and before the runs, so that
the decision rule cannot drift once the numbers are in.

It reads the five partition directories produced by
`02_lambda_sweep_controlled.py --split-seed {0..4}` and prints a verdict for
each criterion. It computes nothing that the pre-registration does not name.

USAGE
-----
    python scripts/03_analise_pre_registrada.py \
        --dirs results/ctl_part0 results/ctl_part1 results/ctl_part2 \
               results/ctl_part3 results/ctl_part4
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

SEP = "=" * 78
ALPHA = 0.05
# H5c: lambda* within one grid step of 1, i.e. in {0.7, 1, 10}
VIZINHANCA_DE_1 = {0.7, 1.0, 10.0}


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def spearman(a, b) -> float:
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def ler_particao(d: Path) -> dict:
    """runs.csv (per seed) + gates.npz (prior and the partition's PLS reference)."""
    with (d / "runs.csv").open() as f:
        runs = list(csv.DictReader(f))
    for r in runs:
        r["lam"] = float(r["lam"])
        r["seed"] = int(r["seed"])
        r["r2"] = float(r["r2"])
        r["agree_pls"] = float(r["agree_pls"])

    z = np.load(d / "gates.npz")
    prior, relevance = z["prior"], z["pls_relevance"]
    return {
        "dir": d,
        "runs": runs,
        "lambdas": sorted({r["lam"] for r in runs}),
        # the prior does not depend on the seed, so this is one number per
        # partition; H5b compares the per-seed gate agreement against it
        "agree_prior": spearman(prior, relevance),
        "pls_h_1se": int(z["pls_h_1se"]),
        "pls_r2": float(z["pls_r2"]),
    }


def por_lambda(runs, lam, campo):
    return np.array([r[campo] for r in sorted(
        (r for r in runs if r["lam"] == lam), key=lambda r: r["seed"])])


def analisar(p: dict) -> dict:
    lams = p["lambdas"]
    medias = {lam: por_lambda(p["runs"], lam, "agree_pls").mean() for lam in lams}
    lam_star = max(lams, key=lambda l: medias[l])

    # H5a: the argmax is not at a grid boundary
    h5a = lam_star not in (lams[0], lams[-1])

    # H5b: agreement at lambda* exceeds the prior's own agreement, paired by seed
    ag = por_lambda(p["runs"], lam_star, "agree_pls")
    d_b = ag - p["agree_prior"]
    p_b = float(wilcoxon(d_b).pvalue)
    h5b = bool(d_b.mean() > 0 and p_b < ALPHA)

    # H5c: lambda* within one grid step of 1
    h5c = lam_star in VIZINHANCA_DE_1

    # H6: lambda* beats lambda=0 on held-out R2, paired by seed
    r2_0 = por_lambda(p["runs"], 0.0, "r2")
    r2_s = por_lambda(p["runs"], lam_star, "r2")
    d_6 = r2_s - r2_0
    p_6 = float(wilcoxon(d_6).pvalue)
    h6 = bool(d_6.mean() > 0 and p_6 < ALPHA)

    return {
        "dir": p["dir"].name, "lam_star": lam_star,
        "agree_prior": p["agree_prior"], "agree_star": ag.mean(),
        "d_b": d_b.mean(), "p_b": p_b,
        "d_6": d_6.mean(), "p_6": p_6,
        "h5a": h5a, "h5b": h5b, "h5c": h5c, "h6": h6,
        "pls_h": p["pls_h_1se"], "pls_r2": p["pls_r2"],
        "r2_star": r2_s.mean(),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    a = ap.parse_args()

    partes = [analisar(ler_particao(Path(d))) for d in a.dirs]
    n = len(partes)

    head(f"Per partition ({n})")
    print(f"{'partition':<16} {'PLS H':>6} {'PLS R2':>7} {'lam*':>6} "
          f"{'agree*':>8} {'prior':>8} {'R2*':>7}  H5a H5b H5c  H6")
    for r in partes:
        v = lambda b: " ok" if b else "  -"
        print(f"{r['dir']:<16} {r['pls_h']:>6} {r['pls_r2']:>7.4f} "
              f"{r['lam_star']:>6g} {r['agree_star']:>+8.4f} "
              f"{r['agree_prior']:>+8.4f} {r['r2_star']:>7.4f} "
              f" {v(r['h5a'])}{v(r['h5b'])}{v(r['h5c'])} {v(r['h6'])}")

    head("Pre-registered verdicts")
    regras = [
        ("H5a", "interior maximum exists", sum(r["h5a"] for r in partes), 4,
         "argmax not at a grid boundary"),
        ("H5b", "beats the prior alone", sum(r["h5b"] for r in partes), 4,
         f"paired Wilcoxon p < {ALPHA}"),
        ("H5c", "position is stable", sum(r["h5c"] for r in partes), 3,
         "lambda* in {0.7, 1, 10}"),
        ("H6 ", "penalty improves accuracy", sum(r["h6"] for r in partes), 4,
         f"paired Wilcoxon p < {ALPHA}"),
    ]
    for nome, desc, k, limiar, como in regras:
        status = "SUPPORTED" if k >= limiar else "NOT SUPPORTED"
        print(f"{nome}  {desc:<28} {k}/{n} partitions (need {limiar})  "
              f"-> {status}")
        print(f"      criterion: {como}")

    h5a_k = sum(r["h5a"] for r in partes)
    h5b_k = sum(r["h5b"] for r in partes)
    head("Reading")
    if h5a_k >= 4 and h5b_k >= 4:
        if sum(r["h5c"] for r in partes) >= 3:
            print("H5 supported in full: an interior maximum exists, it beats the")
            print("prior, and its position transports across partitions.")
        else:
            print("H5a and H5b supported, H5c not: the interior maximum exists and")
            print("beats the prior, but its LOCATION depends on the partition, so")
            print("lambda is not transportable and must be chosen by validation in")
            print("each application. This is the outcome the pre-registration")
            print("anticipated as a result in its own right.")
    else:
        print("H5 not supported. Per the pre-registration, the October finding is")
        print("reported as specific to the partition on which it was measured, and")
        print("described that way in the manuscript.")
    print("\nlambda* per partition:", [r["lam_star"] for r in partes])


if __name__ == "__main__":
    main()
