#!/usr/bin/env python
"""Pre-registered analysis of H7, H8 and H9 (prior control arms).

This script implements, verbatim, the criteria fixed in
`docs/pre-registro-H7-H9.md`. That document was committed (0778970) before any
permuted-prior sweep was executed; this script computes nothing it does not
name, and the grid, the fixed lambda and the thresholds are taken from it
rather than from the numbers.

Pairing check
-------------
With `--init zero` and lam=0 the prior does not enter the loss, so `agree_pls`
at lam=0 must be IDENTICAL across the three arms of one partition. The script
verifies that before printing any verdict: a mismatch means the directories
were paired wrong, or an arm was run on a different split, and the verdicts
would be meaningless.

USAGE
-----
    python scripts/04_analise_controles.py \
        --literature results/ctl_part0 results/ctl_part1 results/ctl_part2 \
                     results/ctl_part3 results/ctl_part4 \
        --blocks     results/ctl_blocks_part0 results/ctl_blocks_part1 \
                     results/ctl_blocks_part2 results/ctl_blocks_part3 \
                     results/ctl_blocks_part4 \
        --shuffled   results/ctl_shuffled_part0 results/ctl_shuffled_part1 \
                     results/ctl_shuffled_part2 results/ctl_shuffled_part3 \
                     results/ctl_shuffled_part4
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

SEP = "=" * 78
ALPHA = 0.05
LAM_FIXO = 1.0          # H7 primary comparison, fixed in the pre-registration
TOL_JACCARD = 0.05      # H9 criterion
TOL_PAREAMENTO = 1e-9   # lam=0 agreement must match exactly across arms
MARGEM_LIMITE = 2e-3    # how close to TOL_JACCARD counts as borderline


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def spearman(a, b) -> float:
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


# --------------------------------------------------------------------- reading

def ler_arm(d: Path) -> dict:
    """One sweep directory. Tolerates the pre-`prior_arm` schema of the
    literature runs, which were produced before the control arms existed."""
    with (d / "runs.csv").open() as f:
        runs = list(csv.DictReader(f))
    for r in runs:
        r["lam"] = float(r["lam"])
        r["seed"] = int(r["seed"])
        r["agree_pls"] = float(r["agree_pls"])
        r["r2"] = float(r["r2"])
        r.setdefault("prior_arm", "literature")

    with (d / "aggregate.csv").open() as f:
        agg = {float(r["lam"]): float(r["jaccard"]) for r in csv.DictReader(f)}

    z = np.load(d / "gates.npz")
    prior, relevance = z["prior"], z["pls_relevance"]
    arms = {r["prior_arm"] for r in runs}
    if len(arms) != 1:
        raise SystemExit(f"{d}: runs.csv mixes arms {arms}")

    return {
        "dir": d,
        "arm": arms.pop(),
        "runs": runs,
        "jaccard": agg,
        "lambdas": sorted({r["lam"] for r in runs}),
        "rho_prior_ref": spearman(prior, relevance),
        "pls_h_1se": int(z["pls_h_1se"]),
        "pls_r2": float(z["pls_r2"]),
    }


def serie(p: dict, lam: float, campo: str = "agree_pls") -> np.ndarray:
    """Values at one lambda, ordered by seed, so arms pair element-wise."""
    sub = sorted((r for r in p["runs"] if r["lam"] == lam),
                 key=lambda r: r["seed"])
    if not sub:
        raise SystemExit(f"{p['dir']}: no runs at lam={lam:g}")
    return np.array([r[campo] for r in sub])


def seeds(p: dict, lam: float) -> list[int]:
    return sorted(r["seed"] for r in p["runs"] if r["lam"] == lam)


def argmax_lam(p: dict) -> float:
    medias = {lam: serie(p, lam).mean() for lam in p["lambdas"]}
    return max(medias, key=lambda l: medias[l])


# ------------------------------------------------------------------- pairing

def conferir_pareamento(lit: dict, ctl: dict) -> None:
    """lam=0 does not use the prior, so the arms must agree there exactly."""
    if seeds(lit, 0.0) != seeds(ctl, 0.0):
        raise SystemExit(
            f"PAIRING: {lit['dir'].name} and {ctl['dir'].name} do not share "
            f"the same model seeds.")
    a, b = serie(lit, 0.0), serie(ctl, 0.0)
    dif = float(np.abs(a - b).max())
    if dif > TOL_PAREAMENTO:
        raise SystemExit(
            f"PAIRING: {lit['dir'].name} vs {ctl['dir'].name}: agreement at "
            f"lam=0 differs by {dif:.3e}, but lam=0 never uses the prior. "
            f"These directories are not the same partition (or one arm was "
            f"run with a different split or --init). Verdicts withheld.")
    if lit["pls_h_1se"] != ctl["pls_h_1se"] or \
            abs(lit["pls_r2"] - ctl["pls_r2"]) > 1e-9:
        raise SystemExit(
            f"PAIRING: {lit['dir'].name} vs {ctl['dir'].name}: different PLS "
            f"reference (H {lit['pls_h_1se']} vs {ctl['pls_h_1se']}). "
            f"Verdicts withheld.")


# ------------------------------------------------------------------- criteria

def par_wilcoxon(d: np.ndarray) -> float:
    """Two-sided Wilcoxon on paired differences; 1.0 if all differences are 0."""
    if np.allclose(d, 0.0):
        return 1.0
    return float(wilcoxon(d).pvalue)


def h7_particao(lit: dict, ctl: dict, lam: float) -> dict:
    """agree(literature) > agree(control), paired by seed."""
    a, b = serie(lit, lam), serie(ctl, lam)
    d = a - b
    p = par_wilcoxon(d)
    return {"lit": a.mean(), "ctl": b.mean(), "delta": d.mean(), "p": p,
            "suportada": bool(d.mean() > 0 and p < ALPHA)}


def h8_particao(ctl: dict) -> dict:
    """Within a control arm: is agree(lam=1) significantly above agree(lam=0)?
    H8 is supported when it is NOT."""
    d = serie(ctl, LAM_FIXO) - serie(ctl, 0.0)
    p = par_wilcoxon(d)
    positiva = bool(d.mean() > 0 and p < ALPHA)
    return {"a0": serie(ctl, 0.0).mean(), "a1": serie(ctl, LAM_FIXO).mean(),
            "delta": d.mean(), "p": p, "suportada": not positiva}


def h9_particao(lit: dict, ctl: dict) -> dict:
    jl, jc = lit["jaccard"][LAM_FIXO], ctl["jaccard"][LAM_FIXO]
    dif = abs(jc - jl)
    return {"lit": jl, "ctl": jc, "dif": jc - jl,
            "suportada": bool(dif < TOL_JACCARD),
            # a difference sitting on the threshold is decided by float noise,
            # so the verdict for that partition is reported, not relied on
            "limite": bool(abs(dif - TOL_JACCARD) < MARGEM_LIMITE)}


def veredito(nome: str, k: int, n: int, limiar: int, como: str) -> bool:
    ok = k >= limiar
    print(f"{nome:<14} {k}/{n} partitions (need {limiar})  "
          f"-> {'SUPPORTED' if ok else 'NOT SUPPORTED'}")
    print(f"{'':14} criterion: {como}")
    return ok


# ----------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--literature", nargs="+", required=True)
    ap.add_argument("--blocks", nargs="+", default=[])
    ap.add_argument("--shuffled", nargs="+", default=[])
    a = ap.parse_args()

    lits = [ler_arm(Path(d)) for d in a.literature]
    ctls = {}
    for nome, dirs in (("blocks", a.blocks), ("shuffled", a.shuffled)):
        if not dirs:
            continue
        if len(dirs) != len(lits):
            raise SystemExit(
                f"--{nome} has {len(dirs)} directories, --literature has "
                f"{len(lits)}. They are paired positionally.")
        ctls[nome] = [ler_arm(Path(d)) for d in dirs]
    if not ctls:
        raise SystemExit("nothing to compare: pass --blocks and/or --shuffled")

    n = len(lits)
    for nome, arms in ctls.items():
        for lit, ctl in zip(lits, arms):
            conferir_pareamento(lit, ctl)
            if ctl["arm"] != nome:
                raise SystemExit(
                    f"{ctl['dir'].name}: runs.csv says arm '{ctl['arm']}', "
                    f"passed as --{nome}.")
    print(f"pairing verified: agreement at lam=0 identical across arms in all "
          f"{n} partitions\n(the prior does not enter the loss there, so this "
          f"would differ if the splits differed)")

    # ------------------------------------------------- the prior vs reference
    head("The prior itself, against the partition's PLS reference")
    print("Spearman(prior, |PLS-1se coefficients|). No model involved: this is")
    print("what each prior is worth before any gate is trained.\n")
    print(f"{'partition':<16} {'PLS H':>6} {'literature':>11}"
          + "".join(f"{k:>11}" for k in ctls))
    for i, lit in enumerate(lits):
        print(f"{lit['dir'].name:<16} {lit['pls_h_1se']:>6} "
              f"{lit['rho_prior_ref']:>+11.4f}"
              + "".join(f"{ctls[k][i]['rho_prior_ref']:>+11.4f}" for k in ctls))

    # ------------------------------------------------------------------- H7
    head(f"H7 - the prior's content matters  (primary, fixed lam={LAM_FIXO:g})")
    resultados = {}
    for nome, arms in ctls.items():
        rs = [h7_particao(lit, ctl, LAM_FIXO) for lit, ctl in zip(lits, arms)]
        resultados[nome] = rs
        print(f"\nliterature vs {nome}")
        print(f"  {'partition':<16} {'lit':>9} {nome:>9} {'delta':>9} "
              f"{'p':>8}   H7")
        for lit, r in zip(lits, rs):
            print(f"  {lit['dir'].name:<16} {r['lit']:>+9.4f} "
                  f"{r['ctl']:>+9.4f} {r['delta']:>+9.4f} {r['p']:>8.4f}   "
                  f"{'ok' if r['suportada'] else '-'}")

    head("H7 verdicts")
    for nome, rs in resultados.items():
        k = sum(r["suportada"] for r in rs)
        veredito(f"H7-{nome}", k, n, 4,
                 f"agree(literature) > agree({nome}) at lam={LAM_FIXO:g}, "
                 f"paired Wilcoxon p < {ALPHA}")
        falhas = n - k
        if falhas >= 2:
            print(f"{'':14} REFUTATION CLAUSE MET: {nome} equals or exceeds "
                  f"literature in {falhas} partitions.")
            if nome == "blocks":
                print(f"{'':14} Per the pre-registration, explanation (b) is "
                      f"the correct reading:")
                print(f"{'':14} the agreement gain does not depend on where "
                      f"the prior points.")
        print()

    # ------------------------------------------------- H7 secondary (argmax)
    head("H7 secondary - each arm at its own argmax (reported, not a verdict)")
    print(f"  {'partition':<16} {'lam* lit':>9} {'agree':>9}"
          + "".join(f" {'lam* ' + k:>10} {'agree':>9}" for k in ctls))
    for i, lit in enumerate(lits):
        ll = argmax_lam(lit)
        linha = (f"  {lit['dir'].name:<16} {ll:>9g} "
                 f"{serie(lit, ll).mean():>+9.4f}")
        for k in ctls:
            c = ctls[k][i]
            lc = argmax_lam(c)
            linha += f" {lc:>10g} {serie(c, lc).mean():>+9.4f}"
        print(linha)

    # ------------------------------------------------------------------- H8
    head("H8 - anchoring alone buys little")
    print(f"Within each control arm: agree(lam={LAM_FIXO:g}) - agree(lam=0), "
          f"paired by seed.")
    print("H8 is SUPPORTED where that difference is NOT significantly "
          "positive.\n")
    for nome, arms in ctls.items():
        rs = [h8_particao(c) for c in arms]
        print(f"{nome}")
        print(f"  {'partition':<16} {'lam=0':>9} {'lam=1':>9} {'delta':>9} "
              f"{'p':>8}   H8")
        for lit, r in zip(lits, rs):
            print(f"  {lit['dir'].name:<16} {r['a0']:>+9.4f} {r['a1']:>+9.4f} "
                  f"{r['delta']:>+9.4f} {r['p']:>8.4f}   "
                  f"{'ok' if r['suportada'] else '-'}")
        k = sum(r["suportada"] for r in rs)
        print()
        veredito(f"H8-{nome}", k, n, 4,
                 f"difference not significantly positive (p >= {ALPHA} or "
                 f"negative)")
        if k < 4:
            print(f"{'':14} H8 NOT supported: anchoring on a content-free "
                  f"prior does raise agreement.")
            print(f"{'':14} Per the pre-registration, anchoring and content "
                  f"must be reported as")
            print(f"{'':14} separate contributions. This does not refute H7.")
        print()

    # ------------------------------------------------------------------- H9
    head("H9 - reproducibility does not depend on content")
    print(f"Pairwise top-decile Jaccard between seeds at lam={LAM_FIXO:g}.\n")
    for nome, arms in ctls.items():
        rs = [h9_particao(lit, ctl) for lit, ctl in zip(lits, arms)]
        print(f"{nome}")
        print(f"  {'partition':<16} {'J lit':>8} {'J ' + nome:>11} "
              f"{'diff':>9}   H9")
        for lit, r in zip(lits, rs):
            print(f"  {lit['dir'].name:<16} {r['lit']:>8.4f} "
                  f"{r['ctl']:>11.4f} {r['dif']:>+9.4f}   "
                  f"{'ok' if r['suportada'] else '-'}"
                  f"{'   <-- on the threshold' if r['limite'] else ''}")
        k = sum(r["suportada"] for r in rs)
        print()
        if any(r["limite"] for r in rs):
            print(f"{'':14} NOTE: a |diff| sitting on {TOL_JACCARD} is decided "
                  f"by floating-point")
            print(f"{'':14} noise, not by the data. Report those partitions by "
                  f"their raw")
            print(f"{'':14} Jaccard values; do not lean on the verdict for "
                  f"them.")
        veredito(f"H9-{nome}", k, n, 4,
                 f"|J(control) - J(literature)| < {TOL_JACCARD}")
        if k >= 4:
            print(f"{'':14} Seed-to-seed stability is reached by a prior whose")
            print(f"{'':14} chemical content was destroyed. Stability "
                  f"therefore does not")
            print(f"{'':14} validate the interpretation: a gate can be "
                  f"perfectly")
            print(f"{'':14} reproducible and point at the wrong bands.")
        print()

    # -------------------------------------------------------------- reading
    head("Reading")
    k_blocks = (sum(r["suportada"] for r in resultados["blocks"])
                if "blocks" in resultados else None)
    if k_blocks is not None and k_blocks < 4:
        print("H7-blocks not supported. The literature prior's POSITION is not")
        print("what produces agreement with the data-derived reference: the "
              "same")
        print("values relocated to random positions do as well or better. What")
        print("remains attributable to the prior is its SHAPE - contiguous")
        print("elevated regions of a given width - which is a smoothness")
        print("constraint, not chemical information.")
        if "shuffled" in resultados:
            k_sh = sum(r["suportada"] for r in resultados["shuffled"])
            if k_sh >= 4:
                print()
                print("H7-shuffled supported, meanwhile: destroying "
                      "contiguity DOES hurt.")
                print("The two arms together localise the mechanism - "
                      "contiguity and")
                print("block width matter, position does not.")
    elif k_blocks is not None:
        print("H7-blocks supported: the agreement gain depends on where the")
        print("prior points, and the chemical reading survives the control.")
    print()


if __name__ == "__main__":
    main()
