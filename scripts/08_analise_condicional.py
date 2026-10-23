#!/usr/bin/env python
"""Pre-registered analysis of H13 (conditioning the metric on the prior).

Implements, verbatim, the criteria fixed in `docs/pre-registro-H13.md`,
committed with this script before any sweep on `--split-seed 10..14`.

The raw whole-spectrum Spearman between gate and |PLS coef| is insensitive to
where the NIR prior points: relocated blocks equal or beat the literature prior
in 9 of the 10 partitions measured up to F003 -- the exception is partition 3,
where literature wins. With a continuous Raman prior the same metric does
distinguish (F005). H13 asks whether removing the prior's own contribution
reveals, in NIR, the signal Raman shows.

Two forms of the same question, both reported, both pre-registered:

  partial  -- first-order partial Spearman rho(g, r | s). Closed form, removes
              the component of the prior that is LINEAR IN RANKS. With a
              four-level prior the ranks are heavily tied, so this removal is
              coarse: it does not eliminate the level structure, only its
              linear part. Declared as a limitation in the document.
  floor    -- Spearman restricted to the prior's floor (223 bands), where the
              prior is constant and contributes exactly zero. Exact, but
              answers only about that level.

Agreement in sign between the two is what makes the reading robust;
disagreement localises the problem in the linear assumption.

USAGE
-----
    python scripts/08_analise_condicional.py \
        --literature results/p10_literature ... results/p14_literature \
        --blocks     results/p10_blocks ... \
        --shuffled   results/p10_shuffled ...
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

SEP = "=" * 78
ALPHA = 0.05
LAM_FIXO = 1.0        # fixed by the pre-registration, not chosen from data
TOL_NIVEL = 1e-9
TOL_PAREAMENTO = 1e-9
MIN_BANDAS_NIVEL = 10


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def spearman_parcial(g, r, s) -> float:
    """rho(g, r | s), first-order partial correlation on ranks.

    Returns nan when either conditioning correlation is degenerate, rather
    than dividing by something near zero."""
    rgr, rgs, rrs = spearman(g, r), spearman(g, s), spearman(r, s)
    if any(np.isnan(x) for x in (rgr, rgs, rrs)):
        return float("nan")
    den = np.sqrt((1.0 - rgs ** 2) * (1.0 - rrs ** 2))
    if den < 1e-12:
        return float("nan")
    return float((rgr - rgs * rrs) / den)


# --------------------------------------------------------------------- reading

def ler(d: Path) -> dict:
    with (d / "runs.csv").open() as f:
        runs = list(csv.DictReader(f))
    for x in runs:
        x["lam"] = float(x["lam"])
        x["seed"] = int(x["seed"])
        x["agree_pls"] = float(x["agree_pls"])
        x.setdefault("prior_arm", "literature")

    z = np.load(d / "gates.npz")
    prior = np.asarray(z["prior"], float)
    chave = f"gates_lam{LAM_FIXO:g}"
    if chave not in z:
        raise SystemExit(f"{d}: {chave} not in gates.npz")
    arms = {x["prior_arm"] for x in runs}
    if len(arms) != 1:
        raise SystemExit(f"{d}: runs.csv mixes arms {arms}")

    niveis, contagens = np.unique(prior, return_counts=True)
    piso = np.flatnonzero(np.abs(prior - prior.min()) <= TOL_NIVEL)
    return {
        "dir": d, "arm": arms.pop(), "runs": runs, "prior": prior,
        "gates": [np.asarray(g, float) for g in z[chave]],
        "gates0": ([np.asarray(g, float) for g in z["gates_lam0"]]
                   if "gates_lam0" in z else None),
        "relevance": np.abs(np.asarray(z["pls_relevance"], float)),
        "p": len(prior), "niveis": niveis, "contagens": contagens,
        "piso": piso, "pls_h_1se": int(z["pls_h_1se"]),
    }


def seeds_de(c: dict, lam: float) -> list[int]:
    return sorted(x["seed"] for x in c["runs"] if x["lam"] == lam)


def agree_cru(c: dict, lam: float) -> np.ndarray:
    sub = sorted((x for x in c["runs"] if x["lam"] == lam),
                 key=lambda x: x["seed"])
    if not sub:
        raise SystemExit(f"{c['dir']}: no runs at lam={lam:g}")
    return np.array([x["agree_pls"] for x in sub])


# -------------------------------------------------------------------- pairing

def conferir(lit: dict, ctl: dict) -> None:
    """At lam=0 the prior does not enter the loss, so the arms of one
    partition must agree there exactly."""
    if seeds_de(lit, 0.0) != seeds_de(ctl, 0.0):
        raise SystemExit(f"PAIRING: {lit['dir'].name} vs {ctl['dir'].name}: "
                         f"different model seeds.")
    dif = float(np.abs(agree_cru(lit, 0.0) - agree_cru(ctl, 0.0)).max())
    if dif > TOL_PAREAMENTO:
        raise SystemExit(
            f"PAIRING: {lit['dir'].name} vs {ctl['dir'].name}: agreement at "
            f"lam=0 differs by {dif:.3e}, but lam=0 never uses the prior. "
            f"Not the same partition. Verdicts withheld.")
    if lit["pls_h_1se"] != ctl["pls_h_1se"]:
        raise SystemExit(
            f"PAIRING: {lit['dir'].name} vs {ctl['dir'].name}: different PLS "
            f"reference (H {lit['pls_h_1se']} vs {ctl['pls_h_1se']}).")


def empatado(gates: list[np.ndarray], bandas=None) -> bool:
    for g in gates:
        v = g if bandas is None else g[bandas]
        if len(np.unique(v)) < len(v):
            return True
    return False


# ------------------------------------------------------------------- statistics

def serie_parcial(c: dict) -> np.ndarray:
    r, s = c["relevance"], c["prior"]
    return np.array([spearman_parcial(g, r, s) for g in c["gates"]])


def serie_rho_gs(c: dict) -> np.ndarray:
    """rho(gate, prior) per seed. The partial statistic divides by
    sqrt(1 - rho_gs^2), so this is how much it amplifies the residual
    correlation: 3.8x at the measured 0.9655, 17x at lambda=10's 0.9983.
    Reported so the reader can judge each cell's amplification instead of
    taking the partial value at face."""
    s = c["prior"]
    return np.array([spearman(g, s) for g in c["gates"]])


def serie_piso(c: dict) -> np.ndarray:
    b = c["piso"]
    r = c["relevance"][b]
    return np.array([spearman(g[b], r) for g in c["gates"]])


def contra_zero(s: np.ndarray) -> dict:
    if np.isnan(s).any():
        return {"indefinida": True}
    p = 1.0 if np.allclose(s, 0) else float(wilcoxon(s).pvalue)
    return {"indefinida": False, "media": float(s.mean()), "p": p,
            "suportada": bool(s.mean() > 0 and p < ALPHA)}


def par(a: np.ndarray, b: np.ndarray) -> dict:
    if np.isnan(a).any() or np.isnan(b).any():
        return {"indefinida": True}
    d = a - b
    p = 1.0 if np.allclose(d, 0) else float(wilcoxon(d).pvalue)
    return {"indefinida": False, "a": float(a.mean()), "b": float(b.mean()),
            "delta": float(d.mean()), "p": p,
            "suportada": bool(d.mean() > 0 and p < ALPHA)}


def veredito(nome: str, k: int, n: int, limiar: int, crit: str,
             indef: int = 0) -> bool:
    extra = f"  ({indef} undefined)" if indef else ""
    ok = k >= limiar
    print(f"{nome:<6} {k}/{n} partitions (need {limiar}){extra}  "
          f"-> {'SUPPORTED' if ok else 'NOT SUPPORTED'}")
    print(f"{'':6} criterion: {crit}")
    return ok


# ----------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--literature", nargs="+", required=True)
    ap.add_argument("--blocks", nargs="+", required=True)
    ap.add_argument("--shuffled", nargs="+", default=[])
    a = ap.parse_args()

    lits = [ler(Path(d)) for d in a.literature]
    blks = [ler(Path(d)) for d in a.blocks]
    if len(blks) != len(lits):
        raise SystemExit("--literature and --blocks pair positionally")
    shfs = [ler(Path(d)) for d in a.shuffled] if a.shuffled else []
    n = len(lits)

    for ctl in (blks, shfs):
        for cl, cc in zip(lits, ctl):
            conferir(cl, cc)
    print(f"pairing verified: agreement at lam=0 identical across arms in all "
          f"{n} partitions")

    head("Setup")
    print(f"{'partition':<18} {'p':>5} {'PLS H':>6} {'levels':>7} "
          f"{'floor':>6}   level sizes")
    for c in lits:
        tam = "  ".join(f"{v:.3g}x{k}" for v, k in
                        zip(c["niveis"], c["contagens"]))
        print(f"{c['dir'].name:<18} {c['p']:>5} {c['pls_h_1se']:>6} "
              f"{len(c['niveis']):>7} {len(c['piso']):>6}   {tam}")
    if any(len(c["piso"]) < MIN_BANDAS_NIVEL for c in lits):
        print(f"\nWARNING: a floor with fewer than {MIN_BANDAS_NIVEL} bands "
              f"does not support a Spearman; H13c would be uninterpretable.")

    # ------------------------------------------------------------------ H13a
    head(f"H13a - partial Spearman is positive (literature, lam={LAM_FIXO:g})")
    print("rho(gate, |PLS coef| | prior), first-order partial on ranks, one")
    print("value per seed, tested against zero.\n")
    print(f"  {'partition':<18} {'mean rho':>9} {'p':>8} {'rho_gs':>8} "
          f"{'amplif':>8}   H13a")
    r13a, ind_a = [], 0
    for c in lits:
        if empatado(c["gates"]):
            r13a.append({"indefinida": True})
            ind_a += 1
            print(f"  {c['dir'].name:<18} {'--':>9} {'--':>8}   UNDEFINED "
                  f"(exact ties)")
            continue
        r = contra_zero(serie_parcial(c))
        r13a.append(r)
        if r["indefinida"]:
            ind_a += 1
            print(f"  {c['dir'].name:<18} {'--':>9} {'--':>8}   UNDEFINED")
        else:
            rgs = float(serie_rho_gs(c).mean())
            amp = (1.0 / np.sqrt(1.0 - rgs ** 2)
                   if abs(rgs) < 1 else float("inf"))
            print(f"  {c['dir'].name:<18} {r['media']:>+9.4f} "
                  f"{r['p']:>8.4f} {rgs:>8.4f} {amp:>7.2f}x   "
                  f"{'ok' if r['suportada'] else '-'}")
    print()
    print("amplif = 1/sqrt(1 - rho_gs^2): how much the partial statistic")
    print("multiplies the residual correlation. Above ~5x read it with care;")
    print("the value is reported, not thresholded, because the criterion is")
    print("the pre-registration's and does not mention amplification.")

    # ------------------------------------------------------------------ H13b
    head(f"H13b - literature beats blocks on the partial statistic")
    print(f"  {'partition':<18} {'lit':>9} {'blocks':>9} {'delta':>9} "
          f"{'p':>8}   H13b")
    r13b, ind_b = [], 0
    for cl, cb in zip(lits, blks):
        if empatado(cl["gates"]) or empatado(cb["gates"]):
            r13b.append({"indefinida": True})
            ind_b += 1
            print(f"  {cl['dir'].name:<18} {'--':>9} {'--':>9} {'--':>9} "
                  f"{'--':>8}   UNDEFINED")
            continue
        r = par(serie_parcial(cl), serie_parcial(cb))
        r13b.append(r)
        if r["indefinida"]:
            ind_b += 1
            print(f"  {cl['dir'].name:<18} {'undefined':>9}")
        else:
            print(f"  {cl['dir'].name:<18} {r['a']:>+9.4f} {r['b']:>+9.4f} "
                  f"{r['delta']:>+9.4f} {r['p']:>8.4f}   "
                  f"{'ok' if r['suportada'] else '-'}")

    # ------------------------------------------------------------------ H13c
    head("H13c - the floor finding, as a primary criterion")
    print("Spearman(gate, |PLS coef|) restricted to the prior's floor, where")
    print("the prior is constant and contributes exactly zero.\n")
    print(f"  {'partition':<18} {'bands':>6} {'mean rho':>9} {'p':>8}   H13c")
    r13c, ind_c = [], 0
    for c in lits:
        if empatado(c["gates"], c["piso"]):
            r13c.append({"indefinida": True})
            ind_c += 1
            print(f"  {c['dir'].name:<18} {len(c['piso']):>6} {'--':>9} "
                  f"{'--':>8}   UNDEFINED (exact ties)")
            continue
        r = contra_zero(serie_piso(c))
        r13c.append(r)
        if r["indefinida"]:
            ind_c += 1
            print(f"  {c['dir'].name:<18} {len(c['piso']):>6} {'--':>9} "
                  f"{'--':>8}   UNDEFINED")
        else:
            print(f"  {c['dir'].name:<18} {len(c['piso']):>6} "
                  f"{r['media']:>+9.4f} {r['p']:>8.4f}   "
                  f"{'ok' if r['suportada'] else '-'}")

    # --------------------------------------------------- secondary analyses
    head("Secondary 1 - the two forms side by side (no verdict)")
    print("Agreement in sign is what makes the reading robust. Disagreement")
    print("localises the problem in the partial statistic's linear assumption.")
    print(f"\n  {'partition':<18} {'partial':>9} {'floor':>9}   same sign")
    for c in lits:
        sp, sf = serie_parcial(c).mean(), serie_piso(c).mean()
        mesmo = "yes" if (sp > 0) == (sf > 0) else "NO"
        print(f"  {c['dir'].name:<18} {sp:>+9.4f} {sf:>+9.4f}   {mesmo}")

    head("Secondary 2 - raw whole-spectrum Spearman, same partitions "
         "(no verdict)")
    print("The comparison raw-vs-conditioned must be made on the SAME data,")
    print("not against the ten earlier partitions.\n")
    cols = [("blocks", blks)] + ([("shuffled", shfs)] if shfs else [])
    print(f"  {'partition':<18} {'lit raw':>9}"
          + "".join(f" {k + ' raw':>12} {'delta':>9}" for k, _ in cols))
    for i, cl in enumerate(lits):
        al = agree_cru(cl, LAM_FIXO)
        linha = f"  {cl['dir'].name:<18} {al.mean():>+9.4f}"
        for _, arms in cols:
            ac = agree_cru(arms[i], LAM_FIXO)
            linha += f" {ac.mean():>+12.4f} {(al - ac).mean():>+9.4f}"
        print(linha)

    if shfs:
        head("Secondary 3 - shuffled on the three statistics (no verdict)")
        print(f"  {'partition':<18} {'partial':>9} {'floor':>9} {'raw':>9}")
        for i, cl in enumerate(lits):
            cs = shfs[i]
            print(f"  {cl['dir'].name:<18} {serie_parcial(cs).mean():>+9.4f} "
                  f"{serie_piso(cs).mean():>+9.4f} "
                  f"{agree_cru(cs, LAM_FIXO).mean():>+9.4f}")

    head("Secondary 4 - the prior itself against the reference (no verdict)")
    print(f"  {'partition':<18} {'literature':>11}"
          + "".join(f"{k:>11}" for k, _ in cols))
    for i, cl in enumerate(lits):
        linha = (f"  {cl['dir'].name:<18} "
                 f"{spearman(cl['prior'], cl['relevance']):>+11.4f}")
        for _, arms in cols:
            linha += f"{spearman(arms[i]['prior'], arms[i]['relevance']):>+11.4f}"
        print(linha)

    # -------------------------------------------------------------- verdicts
    head("Pre-registered verdicts")
    k_a = sum(r.get("suportada", False) for r in r13a)
    k_b = sum(r.get("suportada", False) for r in r13b)
    k_c = sum(r.get("suportada", False) for r in r13c)
    veredito("H13a", k_a, n, 4,
             f"mean partial rho > 0, Wilcoxon p < {ALPHA}", ind_a)
    print()
    veredito("H13b", k_b, n, 4,
             f"literature > blocks on the partial statistic, p < {ALPHA}",
             ind_b)
    print()
    veredito("H13c", k_c, n, 4,
             f"mean within-floor rho > 0, Wilcoxon p < {ALPHA}", ind_c)

    head("Reading")
    if k_b >= 4:
        print("H13b supported: with the prior's contribution removed, the")
        print("literature position does beat a relocated one in NIR. The raw")
        print("whole-spectrum Spearman was confounded by the prior, which is")
        print("why blocks equalled or beat literature in 9 of the 10 earlier")
        print("partitions on it, and it is the same signal Raman shows with a")
        print("continuous prior (F005). Compare against secondary 2 below: the")
        print("raw metric on THESE five partitions is the honest baseline, and")
        print("conditioning only added something if it beats that count.")
        if k_a < 4:
            print()
            print("But H13a NOT supported: the conditioned statistic is not")
            print("itself positive. Read H13b narrowly, as in F003: literature")
            print("beats blocks without aligning with the reference.")
    elif n - k_b >= 2:
        print("H13b not supported: conditioning on the prior does NOT reveal a")
        print("positional signal in NIR. The raw metric's insensitivity was")
        print("therefore not confounding -- the NIR prior carries no positional")
        print("information, and the difference from Raman lies in the priors,")
        print("not in the metrics. Per the pre-registration this is the")
        print("stronger result, because it explains the NIR/Raman discrepancy")
        print("without appealing to a property of the metric.")
    print()
    if k_c >= 4:
        print("H13c supported: the floor finding of F003 replicates on new")
        print("partitions. The gate's data-driven ordering agrees with the")
        print("external reference in the bands the prior demotes.")
        print("This says where the gate finds structure the reference supports;")
        print("it does NOT say the prior is chemically wrong, because the")
        print("reference is a calibrated-PLS proxy and not ground truth.")
    else:
        print("H13c not supported: the floor finding of F003 does not")
        print("replicate, and is reported as specific to the partitions where")
        print("it was observed.")
    print()


if __name__ == "__main__":
    main()
