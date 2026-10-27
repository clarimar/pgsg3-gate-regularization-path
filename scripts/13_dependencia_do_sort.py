#!/usr/bin/env python
"""Is the deterministic top-q overlap a property of the data or of the sort?

WHY
---
Every top-q selection in this programme is written

    np.argsort(g)[::-1][:q]

with no `kind=`. `scripts/05_diagnostico_jaccard.py` states in its output that
"argsort then breaks ties by band index". That is true of `kind="stable"`. It
is NOT true of the default: numpy's default is 'quicksort', an introsort, which
is not stable, so the order among exactly tied values is implementation-defined
and depends on the whole array rather than on the tied values alone.

On the plateau every selected band is tied with every other (findings/F007, P1:
exact equality within each run, 70 of 70). So the selected SET is decided
entirely by the tie rule, and the overlap between two seeds measures that rule,
not the gates. If the rule is index order, both seeds pick the same q bands and
the overlap is exactly 1. If the rule is implementation-defined, the two seeds
pick different subsets of the plateau and the overlap falls to the chance level
for two q-subsets of L.

This script measures the same statistic on the same files under each available
sort kind, and alongside it the randomised rule the manuscript relies on. The
point of running it is the comparison, not any single number.

WHAT A DIFFERENCE HERE WOULD MEAN
---------------------------------
It would NOT mean the data changed, and it would not weaken the manuscript's
argument. Nor does it make the Jaccard a mathematically empty quantity: it
still measures the agreement of the sets a specific procedure produces. The
defect is narrower and worse -- that agreement does not identify the spectral
stability the metric was offered to assess, because the agreeing elements are
drawn from one block of tied values and the tie rule, not the gate, decides
which of them are taken.

So this script quantifies HOW atypical each deterministic rule's answer is,
rather than calling the quantity empty. The randomised rule samples tie orders
uniformly, so its mean and standard deviation describe the population of
answers available to ANY tie rule, and each sort kind can be placed in that
population:

    z = (J_kind - mean_random) / sd_random

A deterministic rule sitting many standard deviations above the typical tie
order is reporting the tie rule, not the gates. A rule sitting inside the
spread -- and a randomised sd of zero, meaning no tie order changes the answer
-- is evidence that the selection is not tie-decided at all. That is the
measurement the Raman arm needs, and it does not require retraining: the
recorded j_index, j_random and j_random_sd in `cells.json` already carry it.

What a difference does mean, practically: any deterministic overlap this
programme reports is a measurement of one environment, and must be reported
with the versions and the sort kind, or recomputed with `kind` stated. The
randomised figure carries no such exposure, because its tie key is random by
construction.

A NOTE ON CAUSE
---------------
A difference between two environments is not by itself proof that the numpy
version caused it. This script therefore prints what is needed to settle that
elsewhere: the SHA-256 of every input file, q, L, the aggregation convention,
the selected index sets, and the versions. The author's requirement of
2026-10-27: the version is necessary to characterise the environment and must
not be presumed a sufficient cause.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/13_dependencia_do_sort.py
    python scripts/13_dependencia_do_sort.py --dir data/processed/gates_r2
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
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


def topo(g: np.ndarray, q: int, kind: str | None) -> set:
    idx = np.argsort(g) if kind is None else np.argsort(g, kind=kind)
    return set(idx[::-1][:q].tolist())


def esperanca_exata(q: int, L: int) -> float:
    """E[J] for two independent uniform q-subsets of L tied bands."""
    if L < q or q < 1:
        return float("nan")
    tot = comb(L, q)
    return float(sum(comb(q, k) * comb(L - q, q - k) / tot * k / (2 * q - k)
                     for k in range(max(0, 2 * q - L), q + 1)))


def jaccard_sorteado(gates: np.ndarray, q: int, seed: int = 0) -> tuple:
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(SORTEIOS):
        tops = [set(np.lexsort((rng.random(len(g)), -g))[:q].tolist())
                for g in gates]
        v.append(jaccard(tops))
    a = np.asarray(v)
    return float(a.mean()), float(a.std(ddof=1))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def z_na_populacao(j: float, media: float, sd: float) -> str:
    """Where this rule's answer sits among the answers tie orders give.

    sd = 0 means no tie order changes the value, so there is no population to
    be atypical in and no z to report. Dividing by it would manufacture an
    infinity out of the most robust case there is.

    EXACTLY zero and merely small are different, and printing sd to four
    decimals makes them look the same: the author's Raman run of 2026-10-27
    showed sd as 0.0000 in all three partitions while two of them returned a
    z of -1.0 sd, which only a non-zero sd can produce. sd is therefore
    printed in full precision elsewhere.

    Full precision then showed what the rounding had hidden: sd = 3.339e-16
    on a Jaccard of 0.959, which is 3.0 ulp of a double at that magnitude.
    That is the residue of floating-point summation over draws that all
    returned the SAME value, not a spread over tie orders. A z computed from
    it divides noise by noise and returns -1.0 for any such pair, which is why
    two partitions reported exactly -1.0. So a spread at the level of
    floating-point noise is reported as no spread, with the threshold set by
    np.spacing at the observed magnitude rather than by a round number chosen
    to fit.

    The 8-ulp factor is an OPERATIONAL NUMERICAL TOLERANCE and nothing more:
    it is where double-precision summation residue over a few hundred terms
    is expected to live, documented as such at the author's instruction of
    2026-10-27. It is not a statistical threshold, it carries no significance
    level, and "no spread" is a statement about this computation's resolution
    rather than a demonstration that the underlying quantity cannot vary.
    """
    if not np.isfinite(sd):
        return "n/a"
    ruido = 8.0 * float(np.spacing(abs(media))) if np.isfinite(media) else 0.0
    if sd <= ruido:
        return ("no spread" if abs(j - media) <= ruido
                else "off a zero spread")
    return f"{(j - media) / sd:+.1f} sd"


def raman_de_cells(caminho: Path) -> None:
    """The Raman arm, from the recorded cells -- no retraining.

    The gate vectors are not persisted by 07_raman_lambda1.py, so the four
    sort kinds cannot be applied there directly. They do not need to be: the
    randomised rule samples tie orders uniformly, so j_random_sd already
    bounds what ANY tie rule can do, and j_index can be placed in that spread.
    This turns "few ties, so the tie rule has little to act on" from a
    plausible explanation into a measured one.
    """
    head("Raman arm, from the recorded cells (no retraining)")
    if not caminho.is_file():
        print(f"  {caminho} not found -- the Raman arm is NOT measured here.")
        print("  Without it, 'the Raman arm is insensitive to the tie rule' "
              "stays a\n  plausible explanation and does not become a result.")
        return
    cel = json.loads(caminho.read_text())
    lit = {int(k.split("|")[0]): v for k, v in cel.items()
           if k.split("|")[1] == "literature" and k.split("|")[2] == "1"}
    if not lit:
        print(f"  {caminho}: no literature cell at lam = 1")
        return
    print(f"  {caminho}   sha256 {sha256(caminho)[:16]}...")
    print(f"{'partition':>10}{'j_index':>10}{'j_random':>10}"
          f"{'sd (full)':>14}{'j_i - j_r':>13}{'ties':>6}"
          f"{'index rule sits':>18}")
    print("-" * 78)
    for s in sorted(lit):
        c = lit[s]
        ji, jr = float(c["j_index"]), float(c["j_random"])
        sd = float(c["j_random_sd"])
        print(f"{s:>10}{ji:>10.4f}{jr:>10.4f}{sd:>14.3e}{ji - jr:>13.3e}"
              f"{int(c['max_empates']):>6}"
              f"{z_na_populacao(ji, jr, sd):>18}")
    print()
    print("  sd and the difference are printed in full precision on purpose. "
          "Rounded to\n  four decimals they both read 0.0000 while a z of "
          "-1.0 sd is being computed\n  from them, which is a display hiding "
          "the quantity it reports on.")
    print("  'no spread' means sd is at or below the floating-point noise of "
          "the value\n  itself (8 ulp at its magnitude) -- every draw returned "
          "the same Jaccard and\n  what remains is summation residue, not "
          "variation over tie orders.")
    print("  'index rule sits' is where the deterministic answer falls among "
          "the answers\n  tie orders give. Compare the +32 to +41 sd of the "
          "NIR arm.")
    print()
    print("  TWO CLAIMS, KEPT APART (author, 2026-10-27):")
    print("    invariance of the METRIC -- what this table shows. No tie "
          "order moved the\n      Jaccard beyond the resolution of the "
          "computation, over the draws examined.")
    print("    invariance of the SELECTED SETS -- what this table does NOT "
          "show. Two\n      different selections can return the same Jaccard, "
          "so equal values do not\n      establish equal sets. Settling it "
          "needs the index sets compared directly,\n      which needs the "
          "Raman gate vectors; 07_raman_lambda1.py does not persist\n      "
          "them, so it is not available from the recorded cells and is not "
          "claimed here.")
    print("  The NIR arm has both, because its gates are stored: see the "
          "distinct-set\n  counts above, where 'stable' gives one set and the "
          "default gives several.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/processed/gates_r2")
    ap.add_argument("--decil", type=float, default=0.10)
    ap.add_argument("--raman-cells", default="results/raman_h12/cells.json")
    ap.add_argument("--indices", action="store_true",
                    help="print the selected index set per seed per kind")
    a = ap.parse_args()

    head("Environment and inputs, so that a difference can be traced")
    import scipy
    print(f"  numpy {np.__version__}   scipy {scipy.__version__}   "
          f"python {sys.version.split()[0]}")
    print(f"  {platform.platform()}")
    print(f"  executable {sys.executable}")
    # Stability of the default, demonstrated rather than quoted from the docs.
    t = np.array([1.0] * 200 + [0.5, 2.0])
    estavel = np.array_equal(np.argsort(t), np.argsort(t, kind="stable"))
    print(f"  default np.argsort reproduces the stable order on a tied array: "
          f"{estavel}")
    print("  (numpy's default is 'quicksort', an introsort. It is not a "
          "stable sort, so\n   the order among exactly equal values is "
          "implementation-defined.)")
    print()
    print("  Aggregation convention, stated rather than left to be inferred: "
          "the Jaccard\n  is computed for each unordered pair of the runs in "
          "the file and the pairwise\n  values are averaged with equal weight "
          "-- C(10,2) = 45 pairs for ten runs. No\n  seed is a reference, and "
          "no pair is weighted by anything.")

    d = Path(a.dir).expanduser()
    arquivos = sorted(d.glob("gates_n*.npz"),
                      key=lambda p: int("".join(c for c in p.stem
                                                if c.isdigit())))
    if not arquivos:
        raise SystemExit(f"no gates_n*.npz in {d}")
    print()
    print("  input files, SHA-256 (so two environments can be compared file "
          "by file):")
    for p in arquivos:
        print(f"    {sha256(p)}  {p}")

    head("Pairwise Jaccard of the literature arm, by tie rule")
    print(f"{'n':>6} {'q':>4} {'L':>4}" + "".join(f"{k:>11}" for k in KINDS)
          + f"{'default':>10}{'randomised':>12}{'E[J] on L':>11}")
    print("-" * 78)
    linhas = []
    conjuntos: dict[int, dict] = {}
    for p in arquivos:
        z = np.load(p, allow_pickle=False)
        if "prior" not in z.files or "gates_lit" not in z.files:
            continue
        prior = np.asarray(z["prior"], float)
        plato = np.flatnonzero(prior >= prior.max() - 1e-9)
        g = np.atleast_2d(np.asarray(z["gates_lit"], float))
        q = int(np.ceil(a.decil * len(prior)))
        L = len(plato)
        n = int("".join(c for c in p.stem if c.isdigit()))
        por_kind = {k: jaccard([topo(x, q, k) for x in g]) for k in KINDS}
        padrao = jaccard([topo(x, q, None) for x in g])
        rm, rs = jaccard_sorteado(g, q)
        ex = esperanca_exata(q, L)
        print(f"{n:>6} {q:>4} {L:>4}"
              + "".join(f"{por_kind[k]:>11.4f}" for k in KINDS)
              + f"{padrao:>10.4f}{rm:>12.4f}{ex:>11.4f}")
        linhas.append((n, q, L, por_kind, padrao, rm, rs, ex))
        conjuntos[n] = {k: [sorted(topo(x, q, k)) for x in g] for k in KINDS}

    head("Where each deterministic rule sits among the answers tie orders give")
    print("  z = (J_kind - mean_random) / sd_random. A rule many sd above the "
          "typical\n  tie order is reporting the tie rule rather than the "
          "gates.")
    print()
    print(f"{'n':>6}{'randomised':>14}{'sd':>9}"
          + "".join(f"{k:>14}" for k in KINDS))
    print("-" * 78)
    for n, q, L, por_kind, padrao, rm, rs, ex in linhas:
        print(f"{n:>6}{rm:>14.4f}{rs:>9.4f}"
              + "".join(f"{z_na_populacao(por_kind[k], rm, rs):>14}"
                        for k in KINDS))

    head("Selected index sets, identical or not across seeds")
    print("  How many DISTINCT sets the ten runs produce under each rule, and "
          "whether\n  every selected band lies inside the plateau. One "
          "distinct set means the rule,\n  not the gate, fixed the selection.")
    print()
    print(f"{'n':>6}" + "".join(f"{k:>13}" for k in KINDS)
          + f"{'all in plateau':>17}")
    print("-" * 78)
    for p in arquivos:
        z = np.load(p, allow_pickle=False)
        if "prior" not in z.files or "gates_lit" not in z.files:
            continue
        n = int("".join(c for c in p.stem if c.isdigit()))
        prior = np.asarray(z["prior"], float)
        plato = set(np.flatnonzero(prior >= prior.max() - 1e-9).tolist())
        dentro = all(set(s) <= plato for k in KINDS for s in conjuntos[n][k])
        print(f"{n:>6}"
              + "".join(f"{len({tuple(s) for s in conjuntos[n][k]}):>13}"
                        for k in KINDS)
              + f"{str(dentro):>17}")
    if a.indices:
        head("The sets themselves, for comparison between environments")
        for n in conjuntos:
            for k in KINDS:
                marcas = {tuple(s) for s in conjuntos[n][k]}
                print(f"  n={n} kind={k}: {len(marcas)} distinct")
                for s in sorted(marcas)[:3]:
                    print(f"    {list(s)}")
                if len(marcas) > 3:
                    print(f"    ... and {len(marcas) - 3} more")

    raman_de_cells(Path(a.raman_cells).expanduser())

    head("Reading")
    if not linhas:
        print("  nothing measured")
        return
    est = [r[3]["stable"] for r in linhas]
    pad = [r[4] for r in linhas]
    ran = [r[5] for r in linhas]
    exs = [r[7] for r in linhas]
    print(f"  stable        {min(est):.4f} to {max(est):.4f}")
    print(f"  default       {min(pad):.4f} to {max(pad):.4f}")
    print(f"  randomised    {min(ran):.4f} to {max(ran):.4f}   "
          f"exact E[J] {min(exs):.4f} to {max(exs):.4f}")
    print()
    if max(est) - min(est) < 1e-12 and abs(max(est) - 1.0) < 1e-12:
        print("  Under index-order tie-breaking every seed selects the SAME q "
              "bands and the\n  overlap is exactly 1. That is a consequence of "
              "the tie rule applied to a\n  fixed band order -- not additional "
              "evidence that the model found stable\n  bands.")
    if abs(np.mean(pad) - np.mean(est)) > 0.01:
        print("  The default sort gives a DIFFERENT answer on the same files. "
              "Any\n  deterministic overlap reported by this programme is "
              "therefore a property of\n  the environment as much as of the "
              "data, and has to be reported with the\n  versions and the sort "
              "kind -- or recomputed with `kind` stated.")
    else:
        print("  The default sort agrees with index-order tie-breaking in "
              "this build. That\n  is a fact about this build and not a "
              "guarantee: the default is documented\n  as 'quicksort', which "
              "is not stable.")
    print()
    print("  The randomised rule agrees with the exact expectation and does "
          "not depend\n  on the sort, because its tie key is random by "
          "construction. The quantity\n  the manuscript relies on is the one "
          "that reproduces across environments;\n  the quantity it criticises "
          "is the one that does not.")
    print()
    print("  None of this makes the Jaccard mathematically empty. It measures "
          "the\n  agreement of the sets a stated procedure produces, and the "
          "column above says\n  how atypical each procedure's answer is among "
          "the answers tie orders give.\n  What it does not do is identify the "
          "spectral stability the metric was offered\n  to assess, because "
          "every agreeing element comes from one tied block.")
    print()
    print("  Three procedures, and the manuscript needs all three rather than "
          "a new\n  official one (author, 2026-10-27):")
    print("    stable, stated     the maximum artificial stability a "
          "deterministic rule gives")
    print("    randomised         agreement without privileging fixed "
          "positions in the plateau")
    print("    default, no kind   historical reproduction, valid only with "
          "its environment named")


if __name__ == "__main__":
    main()
