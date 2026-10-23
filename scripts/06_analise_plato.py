#!/usr/bin/env python
"""Pre-registered analysis of H10 and H11 (within-level agreement, displacement).

Implements, verbatim, the criteria fixed in `docs/pre-registro-H10-H11.md`.
Committed together with that document and before any sweep on
`--split-seed 5..9`, so the decision rule cannot drift once the numbers are in.

Computes nothing the pre-registration does not name. In particular it does not
pick lambda from the data: every primary comparison is at lambda = 1, fixed in
the document.

TIE GUARD
---------
The pre-registration fixes that a cell whose gates are exactly tied inside the
level under analysis is reported as UNDEFINED, never imputed. That guard is
there because the artifact in findings/F002 came from exact ties being read as
ordering. This script enforces it rather than trusting it will not happen.

USAGE
-----
    python scripts/06_analise_plato.py \
        --literature results/p5_lit results/p6_lit results/p7_lit \
                     results/p8_lit results/p9_lit \
        --blocks     results/p5_blocks ... \
        --shuffled   results/p5_shuffled ...
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

SEP = "=" * 78
ALPHA = 0.05
LAM_FIXO = 1.0        # fixed by the pre-registration, not chosen from data
DECIL = 0.10
TOL_NIVEL = 1e-9      # bands within this of a level value belong to it
MIN_BANDAS_NIVEL = 10  # below this a Spearman is reported, never interpreted
FRACAO_H11A = 0.5     # H11a: displacement decile must be under this in plateau


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def topo(v: np.ndarray, q: int) -> np.ndarray:
    return np.argsort(v)[::-1][:q]


def jaccard_medio(vetores: list[np.ndarray], q: int) -> float:
    tops = [set(topo(v, q).tolist()) for v in vetores]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


# --------------------------------------------------------------------- reading

def ler(d: Path) -> dict:
    z = np.load(d / "gates.npz")
    prior = np.asarray(z["prior"], float)
    chave = f"gates_lam{LAM_FIXO:g}"
    if chave not in z:
        raise SystemExit(f"{d}: {chave} not in gates.npz")
    gates = [np.asarray(g, float) for g in z[chave]]

    niveis, contagens = np.unique(prior, return_counts=True)
    plato = np.flatnonzero(prior >= prior.max() - TOL_NIVEL)
    p = len(prior)
    return {
        "dir": d, "prior": prior, "gates": gates,
        "relevance": np.abs(np.asarray(z["pls_relevance"], float)),
        "arm": str(z["prior_arm"]) if "prior_arm" in z else "literature",
        "p": p, "q": int(np.ceil(DECIL * p)),
        "niveis": niveis, "contagens": contagens, "plato": plato,
        "pls_h_1se": int(z["pls_h_1se"]),
    }


# ------------------------------------------------------------------------- H10

def empatado(gates: list[np.ndarray], bandas: np.ndarray) -> bool:
    """Any seed with exact ties inside the level. The pre-registration makes
    this UNDEFINED, not an opportunity to pick another statistic."""
    return any(len(np.unique(g[bandas])) < len(bandas) for g in gates)


def h10_serie(c: dict, bandas: np.ndarray) -> np.ndarray:
    """Within-level Spearman, one value per seed, ordered by seed."""
    ref = c["relevance"][bandas]
    return np.array([spearman(g[bandas], ref) for g in c["gates"]])


def h10a(c: dict, bandas: np.ndarray) -> dict:
    if empatado(c["gates"], bandas):
        return {"indefinida": True}
    s = h10_serie(c, bandas)
    if np.isnan(s).any():
        return {"indefinida": True}
    p = float(wilcoxon(s).pvalue) if not np.allclose(s, 0) else 1.0
    return {"indefinida": False, "media": float(s.mean()), "p": p,
            "suportada": bool(s.mean() > 0 and p < ALPHA)}


def h10b(lit: dict, ctl: dict, bandas_lit: np.ndarray,
         bandas_ctl: np.ndarray) -> dict:
    if empatado(lit["gates"], bandas_lit) or empatado(ctl["gates"], bandas_ctl):
        return {"indefinida": True}
    a, b = h10_serie(lit, bandas_lit), h10_serie(ctl, bandas_ctl)
    if np.isnan(a).any() or np.isnan(b).any():
        return {"indefinida": True}
    d = a - b
    p = float(wilcoxon(d).pvalue) if not np.allclose(d, 0) else 1.0
    return {"indefinida": False, "lit": float(a.mean()), "ctl": float(b.mean()),
            "delta": float(d.mean()), "p": p,
            "suportada": bool(d.mean() > 0 and p < ALPHA)}


# ------------------------------------------------------------------------- H11

def residuo_intra_nivel(c: dict) -> list[np.ndarray]:
    """|gate - mean gate of its own prior level|, per seed.

    NOT |g - s|. The gate is close to an affine function of the prior, so
    |g - s| is largest wherever the prior is lowest, and its top decile lands
    on the 223 floor bands: that moves the confinement from the plateau to the
    floor instead of removing it. Centering each band on the mean gate of its
    own prior level removes the level structure entirely, so a band enters the
    decile by standing out against its own level, and any level can contribute.
    """
    prior = c["prior"]
    grupos = [np.flatnonzero(np.abs(prior - v) <= TOL_NIVEL)
              for v in c["niveis"]]
    saida = []
    for g in c["gates"]:
        r = np.empty_like(g)
        for bandas in grupos:
            r[bandas] = g[bandas] - g[bandas].mean()
        saida.append(np.abs(r))
    return saida


def h11a(c: dict) -> dict:
    d = residuo_intra_nivel(c)
    plato = set(c["plato"].tolist())
    fracoes = [len(set(topo(v, c["q"]).tolist()) & plato) / c["q"] for v in d]
    f = float(np.mean(fracoes))
    return {"fracao": f, "suportada": bool(f < FRACAO_H11A)}


def h11_jaccard(c: dict) -> dict:
    d = residuo_intra_nivel(c)
    empates = [len(v) - len(np.unique(v)) for v in d]
    if max(empates) > 0:
        return {"indefinida": True, "empates": max(empates)}
    return {"indefinida": False, "j": jaccard_medio(d, c["q"])}


def composicao_residuo(c: dict) -> dict:
    """Which prior levels the residual decile draws from. DESCRIPTIVE.

    H11a asks only whether the decile leaves the plateau. It does not ask
    whether the decile is confined somewhere ELSE, and with 223 of 281 bands on
    the floor it can escape the plateau and still be confined. This reports the
    composition against each level's share of bands, so confinement anywhere is
    visible. It is not a criterion and must not become one.
    """
    d = residuo_intra_nivel(c)
    por_nivel = {}
    for v in c["niveis"]:
        bandas = set(np.flatnonzero(
            np.abs(c["prior"] - v) <= TOL_NIVEL).tolist())
        fr = [len(set(topo(x, c["q"]).tolist()) & bandas) / c["q"] for x in d]
        por_nivel[float(v)] = (float(np.mean(fr)), len(bandas) / c["p"])
    return por_nivel


# ----------------------------------------------------------------------- main

def veredito(nome: str, k: int, n: int, limiar: int, como: str,
             indef: int = 0) -> bool:
    ok = k >= limiar
    extra = f"  ({indef} undefined)" if indef else ""
    print(f"{nome:<14} {k}/{n} partitions (need {limiar}){extra}  "
          f"-> {'SUPPORTED' if ok else 'NOT SUPPORTED'}")
    print(f"{'':14} criterion: {como}")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--literature", nargs="+", required=True)
    ap.add_argument("--blocks", nargs="+", required=True)
    ap.add_argument("--shuffled", nargs="+", default=[])
    a = ap.parse_args()

    lits = [ler(Path(d)) for d in a.literature]
    blks = [ler(Path(d)) for d in a.blocks]
    if len(blks) != len(lits):
        raise SystemExit("--literature and --blocks must pair positionally")
    shfs = [ler(Path(d)) for d in a.shuffled] if a.shuffled else []
    n = len(lits)

    head("Setup")
    print(f"{'partition':<16} {'p':>5} {'q':>4} {'PLS H':>6} {'levels':>7} "
          f"{'plateau':>8}   level sizes")
    for c in lits:
        tam = "  ".join(f"{v:.3g}x{k}" for v, k in
                        zip(c["niveis"], c["contagens"]))
        print(f"{c['dir'].name:<16} {c['p']:>5} {c['q']:>4} "
              f"{c['pls_h_1se']:>6} {len(c['niveis']):>7} "
              f"{len(c['plato']):>8}   {tam}")

    # ------------------------------------------------------------------- H10
    head(f"H10a - within-plateau ordering exists (literature, lam={LAM_FIXO:g})")
    print("Spearman(gate, |PLS coef|) over the plateau bands only, one value")
    print("per seed. Inside a level the prior is constant, so between-level")
    print("separation contributes nothing.\n")
    print(f"  {'partition':<16} {'bands':>6} {'mean rho':>9} {'p':>8}   H10a")
    r10a, indef_a = [], 0
    for c in lits:
        r = h10a(c, c["plato"])
        r10a.append(r)
        if r["indefinida"]:
            indef_a += 1
            print(f"  {c['dir'].name:<16} {len(c['plato']):>6} "
                  f"{'--':>9} {'--':>8}   UNDEFINED (exact ties)")
        else:
            print(f"  {c['dir'].name:<16} {len(c['plato']):>6} "
                  f"{r['media']:>+9.4f} {r['p']:>8.4f}   "
                  f"{'ok' if r['suportada'] else '-'}")

    head(f"H10b - literature orders better than blocks (lam={LAM_FIXO:g})")
    print("Each arm on its own plateau, paired by seed.\n")
    print(f"  {'partition':<16} {'lit':>9} {'blocks':>9} {'delta':>9} "
          f"{'p':>8}   H10b")
    r10b, indef_b = [], 0
    for cl, cb in zip(lits, blks):
        r = h10b(cl, cb, cl["plato"], cb["plato"])
        r10b.append(r)
        if r["indefinida"]:
            indef_b += 1
            print(f"  {cl['dir'].name:<16} {'--':>9} {'--':>9} {'--':>9} "
                  f"{'--':>8}   UNDEFINED")
        else:
            print(f"  {cl['dir'].name:<16} {r['lit']:>+9.4f} "
                  f"{r['ctl']:>+9.4f} {r['delta']:>+9.4f} {r['p']:>8.4f}   "
                  f"{'ok' if r['suportada'] else '-'}")

    # ---------------------------------------- H10 secondary: same 34 bands
    head("H10 secondary - both arms on the SAME bands (reported, no verdict)")
    print("The literature plateau, ranked by each arm's gate. Separates which")
    print("bands are in the level from how well they are ordered.\n")
    print(f"  {'partition':<16} {'lit':>9} {'blocks':>9} {'delta':>9} {'p':>8}")
    for cl, cb in zip(lits, blks):
        r = h10b(cl, cb, cl["plato"], cl["plato"])
        if r["indefinida"]:
            print(f"  {cl['dir'].name:<16} {'undefined':>9}")
        else:
            print(f"  {cl['dir'].name:<16} {r['lit']:>+9.4f} "
                  f"{r['ctl']:>+9.4f} {r['delta']:>+9.4f} {r['p']:>8.4f}")

    # ------------------------------------- H10 third: the other prior levels
    head("H10 third - the other prior levels (reported, no verdict)")
    print(f"Levels with fewer than {MIN_BANDAS_NIVEL} bands are printed and "
          f"NOT interpreted.\n")
    for c in lits:
        print(f"  {c['dir'].name}")
        for v, k in zip(c["niveis"], c["contagens"]):
            bandas = np.flatnonzero(np.abs(c["prior"] - v) <= TOL_NIVEL)
            r = h10a(c, bandas)
            nota = "" if k >= MIN_BANDAS_NIVEL else "   <- too few bands"
            if r["indefinida"]:
                print(f"    level {v:.3g}  n={k:<4} undefined{nota}")
            else:
                print(f"    level {v:.3g}  n={k:<4} rho={r['media']:>+7.4f}  "
                      f"p={r['p']:.4f}{nota}")

    # ------------------------------------------------------------------- H11
    head("H11a - the residual decile leaves the plateau (literature)")
    print(f"Top-{lits[0]['q']} of the within-level residual: the fraction of "
          f"it falling")
    print(f"inside the prior's plateau. H11a needs that below "
          f"{FRACAO_H11A}.\n")
    print(f"  {'partition':<16} {'in plateau':>11}   H11a")
    r11a = [h11a(c) for c in lits]
    for c, r in zip(lits, r11a):
        print(f"  {c['dir'].name:<16} {r['fracao']:>11.3f}   "
              f"{'ok' if r['suportada'] else '-'}")

    head("Residual decile composition by prior level (DESCRIPTIVE, no verdict)")
    print("H11a asks only whether the decile leaves the plateau. With 223 of")
    print("281 bands on the floor it can leave the plateau and still be")
    print("confined. 'share' is each level's fraction of all bands: a decile")
    print("drawn without regard to level would match it.\n")
    for c in lits:
        comp = composicao_residuo(c)
        print(f"  {c['dir'].name}")
        for v, (fr, share) in comp.items():
            marca = "   <- confined here" if fr > 0.9 else ""
            print(f"    level {v:.3g}   in decile {fr:.3f}   share {share:.3f}"
                  f"{marca}")

    head("H11b - residual reproducibility distinguishes the arms")
    print("Pairwise top-decile Jaccard of the within-level residual. One")
    print("scalar per cell, so there is no pairing by seed: this criterion is a")
    print("count, and weak by design.\n")
    cols = [("literature", lits), ("blocks", blks)] + \
           ([("shuffled", shfs)] if shfs else [])
    print(f"  {'partition':<16}" + "".join(f"{nome:>12}" for nome, _ in cols)
          + "   H11b")
    r11b, indefinidas = [], []
    for i, c in enumerate(lits):
        vals, linha = {}, f"  {c['dir'].name:<16}"
        for nome, arms in cols:
            r = h11_jaccard(arms[i])
            vals[nome] = None if r["indefinida"] else r["j"]
            if r["indefinida"]:
                linha += f"{'undef':>12}"
                indefinidas.append((c["dir"].name, nome, r.get("empates", 0)))
            else:
                linha += f"{r['j']:>12.4f}"
        ok = (vals["literature"] is not None and vals["blocks"] is not None
              and vals["literature"] > vals["blocks"])
        r11b.append(ok)
        print(linha + f"   {'ok' if ok else '-'}")
    for nome_part, nome_arm, n_emp in indefinidas:
        print(f"\n  undefined: {nome_part} / {nome_arm} has {n_emp} exact ties")
        print("  in the residual, so its decile is partly ordered by the sort.")
        print("  Per the pre-registration the cell is reported, not imputed.")

    # -------------------------------------------------------------- verdicts
    head("Pre-registered verdicts")
    k_a = sum(r.get("suportada", False) for r in r10a)
    veredito("H10a", k_a, n, 4,
             f"mean within-plateau rho > 0, Wilcoxon p < {ALPHA}", indef_a)
    print()
    k_b = sum(r.get("suportada", False) for r in r10b)
    veredito("H10b", k_b, n, 4,
             f"literature > blocks, paired Wilcoxon p < {ALPHA}", indef_b)
    print()
    k_11a = sum(r["suportada"] for r in r11a)
    veredito("H11a", k_11a, n, 4,
             f"displacement decile fraction in plateau < {FRACAO_H11A}")
    print()
    veredito("H11b", sum(r11b), n, 4, "J(literature) > J(blocks)")

    head("Reading")
    # H10a and H10b have to be read together. H10b alone says only that
    # literature beats blocks; it does not say literature is right. An earlier
    # version of this script keyed on H10b alone and printed a conclusion that
    # a failed H10a does not support. The pre-registration did not specify the
    # joint reading either, which is a gap in it, recorded rather than patched.
    if k_b >= 4 and k_a >= 4:
        print("H10a and H10b both supported: inside the plateau the literature")
        print("gate orders bands in agreement with the external reference, and")
        print("better than a relocated prior does. The position carries content,")
        print("visible once the metric looks inside a level instead of across")
        print("levels. H7 stands as refuted on the metric it pre-registered; the")
        print("two together say the whole-spectrum Spearman was insensitive to")
        print("the question it was asked.")
    elif k_b >= 4:
        print("H10b supported but H10a NOT. Read narrowly: literature beats")
        print("blocks without itself ordering in agreement with the reference.")
        print("Relocating the blocks makes the within-plateau ordering worse")
        print("than useless; keeping the literature position leaves it near")
        print("zero with a sign that varies by partition. The position is")
        print("therefore not neutral, but it does not produce alignment, and")
        print("'the prior carries content' is more than these numbers support.")
        print("Check the secondary table: if literature beats blocks on the")
        print("SAME bands in fewer partitions than H10b did, part of H10b is")
        print("set membership rather than ordering.")
    elif n - k_b >= 2:
        print("H10b not supported: the position carries no content even in the")
        print("metric built to see it. Explanation (b) of H7 is confirmed by a")
        print("second, independent route - a stronger result than H7 alone.")
    if k_11a < 4:
        print()
        print("H11a not supported: the displacement decile stays inside the")
        print("plateau too, so displacement did not solve the confinement and")
        print("H11b must not be read. Per the pre-registration, that is the")
        print("outcome, not a cue to try a third metric on these data.")
    elif sum(r11b) < 4:
        print()
        print("H11a supported, H11b not: a metric that does leave the plateau")
        print("fails to distinguish the arms. That reinforces, rather than")
        print("weakens, the reading that the stability credited to the prior")
        print("follows from restricting the candidate set.")
    print()


if __name__ == "__main__":
    main()
