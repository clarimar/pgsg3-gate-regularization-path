#!/usr/bin/env python
"""Why the Jaccard numbers come out where they do. DESCRIPTIVE, not a test.

H9-blocks came out NOT SUPPORTED while H9-shuffled came out SUPPORTED, and the
literature arm reached J = 1.0000 in two partitions. This script explains those
three facts from the gates already on disk. It tests no hypothesis, has no
criterion and no verdict: it is read alongside `04_analise_controles.py`, never
in place of it, and nothing here may be turned into a post-hoc criterion.

The mechanism it measures
-------------------------
The prior is min-max normalized, so it has a FLAT PLATEAU at its maximum. The
top-decile metric keeps q = ceil(0.10 p) bands. When the plateau is larger than
q, the prior cannot decide which of its own plateau bands make the cut -- the
DATA breaks those ties. So:

  * J = 1.0 means the same q bands won in every seed: churn = q.
  * A lower J means the data broke the ties differently across seeds.

That is a property of plateau size against q, not of chemistry, and it is why
a Jaccard can be high while agreement with an external reference is poor.

USAGE
-----
    python scripts/05_diagnostico_jaccard.py \
        --dirs results/ctl_part0 results/ctl_blocks_part0 \
               results/ctl_shuffled_part0 --lam 1
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

SEP = "=" * 78
# a band counts as on the plateau if it is within this of the prior's maximum
TOL_PLATO = 1e-9


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def spearman(a, b) -> float:
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def topo(g: np.ndarray, q: int) -> np.ndarray:
    return np.argsort(g)[::-1][:q]


def jaccard_medio(gates: list[np.ndarray], q: int) -> float:
    tops = [set(topo(g, q).tolist()) for g in gates]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


def diagnosticar(d: Path, lam: float, decil: float) -> dict:
    z = np.load(d / "gates.npz")
    prior = z["prior"]
    relevance = (np.asarray(z["pls_relevance"], dtype=np.float64)
                 if "pls_relevance" in z else None)
    p = len(prior)
    q = int(np.ceil(decil * p))

    chave = f"gates_lam{lam:g}"
    if chave not in z:
        raise SystemExit(f"{d}: {chave} not in gates.npz "
                         f"(have: {[k for k in z if k.startswith('gates_')]})")
    gates = [np.asarray(g, dtype=np.float64) for g in z[chave]]
    gates0 = ([np.asarray(g, dtype=np.float64) for g in z["gates_lam0"]]
              if "gates_lam0" in z else None)

    # the prior's plateau: bands tied at its maximum
    plato = np.flatnonzero(prior >= prior.max() - TOL_PLATO)
    # exact ties anywhere in the prior, which is what forces the data to decide
    niveis, contagens = np.unique(prior, return_counts=True)
    n_empatados = int(contagens[contagens > 1].sum())

    tops = [set(topo(g, q).tolist()) for g in gates]
    uniao = set().union(*tops)
    intersecao = set.intersection(*tops)

    # how much of the decile the plateau alone already fixes
    dentro = [len(t & set(plato.tolist())) / q for t in tops]

    # does the data-only gate (lam=0) predict which plateau bands win at lam?
    # if it does, the ties are being broken by signal, not by noise.
    corr_dados = float("nan")
    if gates0 is not None and len(plato) > 2:
        venceu = np.array([sum(b in t for t in tops) for b in plato],
                          dtype=float)
        forca0 = np.array([np.mean([g[b] for g in gates0]) for b in plato])
        corr_dados = spearman(forca0, venceu)

    # Which plateau bands hold a decile slot in EVERY seed, and which do not.
    # This is the comparison the Spearman above summarises, stated so it can
    # be read directly: with 29 slots for 34 tied bands, the question is which
    # five or six lose, and whether the data-only gate had elevated them.
    sempre, as_vezes = [], []
    for b in plato:
        (sempre if all(b in t for t in tops) else as_vezes).append(int(b))
    forca = (lambda bs: float(np.mean([np.mean([g[b] for g in gates0])
                                       for b in bs])) if gates0 and bs
             else float("nan"))
    p_mw = float("nan")
    if gates0 is not None and len(sempre) > 1 and len(as_vezes) > 1:
        from scipy.stats import mannwhitneyu
        xs = [np.mean([g[b] for g in gates0]) for b in sempre]
        ys = [np.mean([g[b] for g in gates0]) for b in as_vezes]
        p_mw = float(mannwhitneyu(xs, ys, alternative="two-sided").pvalue)

    # The same question against an EXTERNAL reference. The lam=0 gate is this
    # architecture's own output, so using it to say "the data wanted this band"
    # closes a loop through the very model under examination. |PLS-1se coef|
    # is computed on the training split by a different estimator, so it breaks
    # that loop. The two columns answer the same question independently.
    corr_pls = float("nan")
    rel_sempre = rel_as_vezes = p_mw_pls = float("nan")
    if relevance is not None and len(plato) > 2:
        venceu = np.array([sum(b in t for t in tops) for b in plato],
                          dtype=float)
        corr_pls = spearman(np.abs(relevance[plato]), venceu)
    if relevance is not None and len(sempre) > 1 and len(as_vezes) > 1:
        from scipy.stats import mannwhitneyu
        xs = np.abs(relevance[sempre])
        ys = np.abs(relevance[as_vezes])
        rel_sempre, rel_as_vezes = float(xs.mean()), float(ys.mean())
        p_mw_pls = float(mannwhitneyu(xs, ys, alternative="two-sided").pvalue)

    return {
        "dir": d.name, "p": p, "q": q,
        "plato": len(plato), "empatados": n_empatados,
        "niveis": int(len(niveis)), "maior_grupo": int(contagens.max()),
        "jaccard": jaccard_medio(gates, q),
        "churn": len(uniao), "nucleo": len(intersecao),
        "dentro_plato": float(np.mean(dentro)),
        "corr_dados": corr_dados, "corr_pls": corr_pls,
        "n_sempre": len(sempre), "n_as_vezes": len(as_vezes),
        "forca_sempre": forca(sempre), "forca_as_vezes": forca(as_vezes),
        "p_mw": p_mw,
        "rel_sempre": rel_sempre, "rel_as_vezes": rel_as_vezes,
        "p_mw_pls": p_mw_pls,
        "niveis_valores": [(float(v), int(c))
                           for v, c in zip(niveis, contagens)],
        "gate_max_ties": int((np.abs(gates[0] - gates[0].max()) < 1e-12).sum()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--lam", type=float, default=1.0)
    ap.add_argument("--decil", type=float, default=0.10)
    a = ap.parse_args()

    rs = [diagnosticar(Path(d), a.lam, a.decil) for d in a.dirs]

    head(f"Top-decile composition at lam={a.lam:g}")
    print(f"q = ceil({a.decil} x p) bands kept.  plateau = bands tied at the")
    print("prior's maximum.  churn = bands appearing in ANY seed's decile;")
    print("core = bands in EVERY seed's decile.  churn = q  <=>  J = 1.\n")
    print(f"{'directory':<26} {'p':>4} {'q':>4} {'plateau':>8} {'ties':>6} "
          f"{'levels':>7} {'J':>7} {'churn':>6} {'core':>5} {'in plat':>8} "
          f"{'rho data':>9} {'rho pls':>8}")
    for r in rs:
        print(f"{r['dir']:<26} {r['p']:>4} {r['q']:>4} {r['plato']:>8} "
              f"{r['empatados']:>6} {r['niveis']:>7} {r['jaccard']:>7.4f} "
              f"{r['churn']:>6} {r['nucleo']:>5} {r['dentro_plato']:>8.3f} "
              f"{r['corr_dados']:>9.3f} {r['corr_pls']:>8.3f}")

    head("The prior's levels")
    print("A prior with few distinct values is a step function, and then the "
          "only")
    print("information it carries is where the steps are and how wide. Each "
          "level is")
    print("printed with the number of bands holding it.\n")
    for r in rs:
        niveis = "   ".join(f"{v:.4g} x{c}" for v, c in r["niveis_valores"][:8])
        resto = ("   ..." if len(r["niveis_valores"]) > 8 else "")
        print(f"{r['dir']:<26} {r['niveis']:>3} levels:  {niveis}{resto}")

    head("Which plateau bands lose, and had the data wanted them?")
    print("The decile has q slots for a plateau of tied bands. 'always' holds "
          "a slot in")
    print("every seed, 'sometimes' does not. The gate at lam=0 is the "
          "data-only gate:")
    print("it starts at 0.5 for every band, so a value above 0.5 means the "
          "data pushed")
    print("that band UP when nothing was anchoring it.\n")
    print("The last three columns ask the same question of |PLS-1se coef|, a")
    print("reference from a different estimator, so the answer does not come "
          "from")
    print("the gate model's own output.\n")
    print(f"{'directory':<26} {'always':>7} {'somet.':>7} "
          f"{'g0 alw':>8} {'g0 som':>8} {'p':>7}   "
          f"{'pls alw':>9} {'pls som':>9} {'p':>7}")
    for r in rs:
        print(f"{r['dir']:<26} {r['n_sempre']:>7} {r['n_as_vezes']:>7} "
              f"{r['forca_sempre']:>8.4f} {r['forca_as_vezes']:>8.4f} "
              f"{r['p_mw']:>7.4f}   "
              f"{r['rel_sempre']:>9.4g} {r['rel_as_vezes']:>9.4g} "
              f"{r['p_mw_pls']:>7.4f}")

    head("Reading")
    for r in rs:
        if r["gate_max_ties"] > 1:
            print(f"{r['dir']}: {r['gate_max_ties']} trained gate values are "
                  f"exactly tied at the maximum.")
            print("  argsort then breaks ties by band index, so this Jaccard "
                  "is partly an")
            print("  artifact of ordering. Report it only with that stated.")
    if all(r["gate_max_ties"] <= 1 for r in rs):
        print("No exact ties among trained gate values: the deciles are "
              "ordered by the")
        print("gates themselves, so J = 1 means genuine agreement across "
              "seeds, not")
        print("tie-breaking by band index.")
    print()
    for r in rs:
        folga = r["plato"] - r["q"]
        if folga > 0:
            print(f"{r['dir']}: plateau ({r['plato']}) exceeds q ({r['q']}) by "
                  f"{folga}. The prior cannot")
            print(f"  choose among its own top bands; the data picks "
                  f"{r['q']} of {r['plato']}. Churn "
                  f"{r['churn']} means")
            print(f"  {r['churn'] - r['q']} band(s) beyond a perfectly stable "
                  f"decile changed hands across seeds.")
        elif r["plato"] > 0:
            print(f"{r['dir']}: plateau ({r['plato']}) does not exceed q "
                  f"({r['q']}), so the decile is not")
            print("  decided inside a tie and this mechanism does not apply "
                  "here.")
    print()
    print("rho data is the Spearman correlation, over plateau bands, between")
    print("how strong the band is in the lam=0 (data-only) gate and how often "
          "it wins")
    print("a decile slot at this lam. Three cases, and the third is not the")
    print("absence of the other two:")
    print("  positive  -- ties broken by signal: the bands the data liked are "
          "the ones")
    print("               the decile keeps.")
    print("  near zero -- ties broken by seed noise: the Jaccard measures how "
          "little")
    print("               room the plateau left, not what the model learned.")
    print("  NEGATIVE  -- ties broken AGAINST signal: the plateau bands the "
          "data-only")
    print("               gate elevated are the ones the decile DROPS. The "
          "selected")
    print("               bands are then the ones the regressor is indifferent "
          "to, which")
    print("               the penalty can hold at the ceiling unopposed. A "
          "stable decile")
    print("               of bands that carry no signal is still stable, so a "
          "high Jaccard")
    print("               is consistent with this and does not rule it out.")
    print()
    print("rho pls asks the same of |PLS-1se coef| instead of the lam=0 gate.")
    print("It matters because rho data uses this architecture's own gate to "
          "decide")
    print("what the data wanted, which is circular; the PLS reference is not.")
    print("The two agreeing in sign is what makes the reading hold. The two")
    print("disagreeing means the effect lives in the gate model and not in the")
    print("data, and must be reported that way.")
    for r in rs:
        if not np.isnan(r["corr_dados"]) and r["corr_dados"] < -0.15:
            print()
            print(f"{r['dir']}: rho data = {r['corr_dados']:+.3f}, the third "
                  f"case. Read the table above:")
            print(f"  g0 for the bands that always hold a slot is "
                  f"{r['forca_sempre']:.4f}; for the bands that")
            print(f"  lose a slot it is {r['forca_as_vezes']:.4f} "
                  f"(Mann-Whitney p = {r['p_mw']:.4f}).")
            if np.isnan(r["corr_pls"]):
                print("  rho pls could not be computed, so this rests on the "
                      "gate alone.")
            elif r["corr_pls"] < -0.15:
                print(f"  rho pls = {r['corr_pls']:+.3f} agrees in sign: the "
                      f"external reference also")
                print(f"  ranks the losing plateau bands above the ones that "
                      f"keep a slot.")
            elif r["corr_pls"] > 0.15:
                print(f"  rho pls = {r['corr_pls']:+.3f} DISAGREES in sign. "
                      f"The effect is a property of")
                print(f"  the gate model, not of the data. Do not state it as "
                      f"a fact about bands.")
            else:
                print(f"  rho pls = {r['corr_pls']:+.3f} is near zero: the "
                      f"external reference does not")
                print(f"  corroborate it, so the claim rests on the gate's own "
                      f"lam=0 output.")
    print()
    print("All of this is descriptive. None of it is a criterion, and nothing "
          "here")
    print("may be turned into one after the fact.")


if __name__ == "__main__":
    main()
