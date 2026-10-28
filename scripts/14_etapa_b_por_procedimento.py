#!/usr/bin/env python
"""Every affected number of Section 4 and Section 6, per selection procedure.

WHY
---
findings/F008 established that the deterministic top-q overlap is a property of
the tie rule and not of the gates whenever the selected set lies inside a tied
level. Stage B of the revision therefore cannot report one number: each number
has to name the procedure that produced it. The author's instruction of
2026-10-27: the contribution is the COMPARISON between procedures, not the
replacement of the historical value by J = 1 or by J = 0.744.

This script produces that comparison from versioned artefacts only, with no
retraining, for:

  Section 4.2.1  the overlap across the seven training sizes, per procedure
  Section 5      the association with sample size, per procedure, for both
                 the prior-initialised arm and the theta_0 = 0 arm
  Section 6      the control-arm overlaps, per procedure, for any directory
                 holding a gates.npz -- which is where 0.9763 to 1.0000 came
                 from and where its sensitivity has to be checked before the
                 interpretation is touched

WHAT DECIDES SECTION 6 WITHOUT A JUDGEMENT CALL
-----------------------------------------------
A tie rule can only reorder values that are exactly equal. If no exact tie
exists among the selected values, every rule returns the same set and the
number is rule-invariant as a matter of arithmetic rather than of inspection.
So this script counts exact ties among the top-q values and reports whether
any tie group straddles the selection boundary at rank q. A boundary with no
tie on it cannot be moved by any rule, and that is the whole question for the
control arms, which run at theta_0 = 0 and should carry no saturation.

THE UNIT OF REPLICATION, WHICH NO CORRELATION HERE ESCAPES
----------------------------------------------------------
The seven training sizes are nested subsamples of one collection of 725
fruits, and the ten runs within a size share that size's training set. So a
correlation across sizes has seven points that are not independent draws from
a population of datasets, and a test over the ten runs characterises the
optimisation procedure conditional on the data. Every association printed
below is therefore EXPLORATORY, and the script says so next to each one rather
than leaving it to the reader. This is the author's requirement of
2026-10-27 and it is not a hedge: no justification for the inferential
reading is available from these artefacts.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/14_etapa_b_por_procedimento.py
    python scripts/14_etapa_b_por_procedimento.py --dirs results/p*  --lam 1
"""

from __future__ import annotations

import argparse
import itertools
import sys
from math import comb
from pathlib import Path

import numpy as np

SEP = "=" * 78
KINDS = ("quicksort", "heapsort", "mergesort", "stable")
SORTEIOS = 200


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def jaccard(tops: list[set]) -> float:
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


def topo(g: np.ndarray, q: int, kind: str) -> set:
    return set(np.argsort(g, kind=kind)[::-1][:q].tolist())


def esperanca_exata(q: int, L: int) -> float:
    if L < q or q < 1:
        return float("nan")
    tot = comb(L, q)
    return float(sum(comb(q, k) * comb(L - q, q - k) / tot * k / (2 * q - k)
                     for k in range(max(0, 2 * q - L), q + 1)))


def jaccard_sorteado(gates: np.ndarray, q: int, seed: int = 0) -> tuple:
    rng = np.random.default_rng(seed)
    v = [jaccard([set(np.lexsort((rng.random(len(g)), -g))[:q].tolist())
                  for g in gates]) for _ in range(SORTEIOS)]
    a = np.asarray(v)
    return float(a.mean()), float(a.std(ddof=1))


def empate_na_fronteira(g: np.ndarray, q: int) -> tuple[int, bool]:
    """Exact ties among the selected values, and whether one sits ON the
    boundary at rank q.

    The second is what decides rule-dependence. Ties strictly inside the
    selected set do not change WHICH bands are selected; only a tie group
    spanning rank q does, because then the rule picks which of its members
    are taken. Reported separately, because 'there are ties' and 'the
    selection is rule-dependent' are different statements.
    """
    ord_desc = np.sort(g)[::-1]
    sel = ord_desc[:q]
    _, cont = np.unique(sel, return_counts=True)
    empates = int(cont[cont > 1].sum())
    na_fronteira = bool(q < len(ord_desc) and ord_desc[q - 1] == ord_desc[q])
    return empates, na_fronteira


def spearman(a, b) -> float:
    from scipy.stats import rankdata
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.size < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def por_procedimento(g: np.ndarray, q: int) -> dict:
    d = {k: jaccard([topo(x, q, k) for x in g]) for k in KINDS}
    d["default"] = jaccard([set(np.argsort(x)[::-1][:q].tolist()) for x in g])
    m, s = jaccard_sorteado(g, q)
    d["randomised"], d["randomised_sd"] = m, s
    emp = [empate_na_fronteira(x, q) for x in g]
    d["ties_in_top"] = max(e[0] for e in emp)
    d["tie_on_boundary"] = sum(e[1] for e in emp)
    d["runs"] = len(g)
    return d


def bloco_gates_r2(d: Path, decil: float) -> None:
    arquivos = sorted(d.glob("gates_n*.npz"),
                      key=lambda p: int("".join(c for c in p.stem
                                                if c.isdigit())))
    if not arquivos:
        print(f"  no gates_n*.npz in {d}")
        return
    series: dict[str, list] = {}
    ns = []
    for arm in ("gates_lit", "gates_rand"):
        head(f"Section 4.2.1 and 5 -- arm {arm}, by procedure")
        print(f"{'n':>6}{'q':>4}{'ties':>6}{'bnd':>5}"
              + "".join(f"{k:>11}" for k in KINDS)
              + f"{'default':>10}{'random':>9}{'E[J]':>8}")
        print("-" * 78)
        ns = []
        vals: dict[str, list] = {k: [] for k in
                                 list(KINDS) + ["default", "randomised"]}
        for p in arquivos:
            z = np.load(p, allow_pickle=False)
            if arm not in z.files or "prior" not in z.files:
                continue
            prior = np.asarray(z["prior"], float)
            plato = np.flatnonzero(prior >= prior.max() - 1e-9)
            g = np.atleast_2d(np.asarray(z[arm], float))
            q = int(np.ceil(decil * len(prior)))
            n = int("".join(c for c in p.stem if c.isdigit()))
            r = por_procedimento(g, q)
            ns.append(n)
            for k in vals:
                vals[k].append(r[k])
            print(f"{n:>6}{q:>4}{r['ties_in_top']:>6}"
                  f"{r['tie_on_boundary']:>5}"
                  + "".join(f"{r[k]:>11.4f}" for k in KINDS)
                  + f"{r['default']:>10.4f}{r['randomised']:>9.4f}"
                  f"{esperanca_exata(q, len(plato)):>8.4f}")
        series[arm] = (ns, vals)
        print()
        print("  'ties' is the largest number of exactly tied values inside "
              "the selected\n  set, in any run; 'bnd' is how many of the runs "
              "have a tie group sitting ON\n  the boundary at rank q. Only the "
              "second makes the SELECTION rule-dependent.")

    head("Section 5 -- association with sample size, per procedure")
    print("  EXPLORATORY in every row. Seven nested subsamples of one "
          "collection of 725\n  fruits are not independent draws, so no "
          "inferential reading is available\n  from these artefacts (author, "
          "2026-10-27).")
    print()
    print(f"{'arm':<12}{'procedure':<14}{'range':>20}{'Spearman vs n':>16}")
    print("-" * 78)
    for arm, (ns, vals) in series.items():
        for k in ("stable", "default", "randomised"):
            v = vals[k]
            if not v:
                continue
            faixa = (f"constant {v[0]:.4f}" if np.ptp(v) < 5e-5
                     else f"{min(v):.4f} to {max(v):.4f}")
            rho = spearman(ns, v)
            texto = ("undefined (constant)" if not np.isfinite(rho)
                     else f"{rho:+.4f}")
            print(f"{arm:<12}{k:<14}{faixa:>20}{texto:>16}")
    print()
    print("  A procedure whose series is constant has no association to "
          "report, and that\n  is a result rather than a missing value: under "
          "index-order tie-breaking the\n  overlap is 1 at every sample size.")


def bloco_controles(dirs: list[Path], lam: float, decil: float) -> None:
    head("Section 6 -- control arms, by procedure")
    print("  These runs use theta_0 = 0, so no gate is saturated and the "
          "selected values\n  should carry no exact ties. Where the boundary "
          "at rank q carries no tie, no\n  rule can move the selection and the "
          "number is rule-invariant as arithmetic,\n  not as judgement.")
    print()
    print(f"{'directory':<26}{'arm':<14}{'q':>4}{'ties':>6}{'bnd':>5}"
          + "".join(f"{k:>10}" for k in ("stable", "default", "random")))
    print("-" * 78)
    achou = 0
    com_fronteira: list[str] = []
    discordantes: list[str] = []
    ausentes: list[str] = []
    for d in dirs:
        z_path = d / "gates.npz"
        if not z_path.is_file():
            print(f"{str(d):<26}no gates.npz")
            ausentes.append(str(d))
            continue
        z = np.load(z_path, allow_pickle=False)
        chave = f"gates_lam{lam:g}"
        if chave not in z.files:
            print(f"{str(d):<26}{chave} absent; has "
                  f"{[k for k in z.files if k.startswith('gates_lam')]}")
            ausentes.append(str(d))
            continue
        achou += 1
        prior = np.asarray(z["prior"], float)
        g = np.atleast_2d(np.asarray(z[chave], float))
        q = int(np.ceil(decil * len(prior)))
        r = por_procedimento(g, q)
        if r["tie_on_boundary"]:
            com_fronteira.append(str(d))
        espalho = max(abs(r[k] - r["stable"])
                      for k in ("default", "randomised", *KINDS))
        if espalho > 5e-5:
            discordantes.append(f"{d} (spread {espalho:.4f})")
        print(f"{str(d):<26}{chave:<14}{q:>4}{r['ties_in_top']:>6}"
              f"{r['tie_on_boundary']:>5}"
              f"{r['stable']:>10.4f}{r['default']:>10.4f}"
              f"{r['randomised']:>10.4f}")
    if not achou:
        print("\n  Nothing measured. Section 6's own numbers come from the "
              "partition\n  directories; point --dirs at them.")
        return
    print()
    print("  Where 'bnd' is 0 in every run, the three columns must agree "
          "exactly, and\n  Section 6's figures need no qualification by sort "
          "kind. Where it is not 0,\n  they need the same treatment as "
          "Section 4.")
    # One-line verdict, last, so that `| tail` cannot hide a non-zero bnd in a
    # long directory listing. The author's run of 2026-10-27 was truncated to
    # the last 20 lines and the per-directory rows that mattered were above
    # the cut: a check whose conclusion can be cropped off is not a check.
    print()
    print(f"  SECTION 6 VERDICT over {achou} directories at lam = {lam:g}:")
    if com_fronteira:
        print(f"    TIE ON THE BOUNDARY in {len(com_fronteira)}: "
              f"{', '.join(com_fronteira)}")
        print("    Section 6 is NOT rule-invariant and needs Section 4's "
              "treatment there.")
    else:
        print(f"    no tie group on the selection boundary in any run of any "
              f"of the {achou}")
    if discordantes:
        print(f"    PROCEDURES DISAGREE in {len(discordantes)}: "
              f"{', '.join(discordantes)}")
    else:
        print(f"    every procedure returns the same figure to within 5e-5 "
              f"in all {achou}")
    if ausentes:
        print(f"    NOT MEASURED in {len(ausentes)}: {', '.join(ausentes)} "
              f"-- these are not covered by the verdict")
    print("    => rule-invariant" if not (com_fronteira or discordantes)
          else "    => NOT established; see the lines above")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/processed/gates_r2")
    ap.add_argument("--dirs", nargs="*", default=None,
                    help="directories holding gates.npz, for Section 6")
    ap.add_argument("--lam", type=float, default=1.0)
    ap.add_argument("--decil", type=float, default=0.10)
    a = ap.parse_args()

    head("Stage B: every affected number, by selection procedure")
    import scipy
    print(f"  numpy {np.__version__}   scipy {scipy.__version__}   "
          f"python {sys.version.split()[0]}")
    print("  The default column is this environment's default and is NOT "
          "portable; it is\n  reported so the historical value can be "
          "reproduced where it was obtained.")

    bloco_gates_r2(Path(a.dir).expanduser(), a.decil)

    padrao = ["results/ctl_adam", "results/ctl_adamw", "results/ctl_piloto"]
    dirs = [Path(x).expanduser() for x in (a.dirs if a.dirs else padrao)]
    bloco_controles(dirs, a.lam, a.decil)

    head("What this settles and what it does not")
    print("  Settles: which number belongs to which procedure, and whether "
          "each one is\n  rule-dependent at all -- by the tie on the "
          "boundary, not by inspection.")
    print("  Does not settle: whether any of the associations with sample "
          "size supports\n  inference. The replication unit does not allow "
          "it from these artefacts.")
    print("  Does not settle: identity of selected sets wherever the gates "
          "are not stored.")


if __name__ == "__main__":
    main()
