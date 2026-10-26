#!/usr/bin/env python
"""Does the displacement control depend on the prior's plateau?

WHY
---
The accepted manuscript answers the objection that the prior merely immobilises
the gate by measuring the DISPLACEMENT d = g_final - g_0 and reporting its
reproducibility across seeds, rho(d) = 0.9462 in NIR. `findings/F002` shows the
top-decile overlap in that arm to be tie order; the displacement control applies
no selection operator and has no arbitrary ordering, so it is immune to THAT
defect. `docs/adr/ADR-0003` records that this is what supports the earlier
paper's interpretive claim, and it is why the claim stands.

This script asks a different question, which the program has not examined.

Under the prior in the initialisation, theta_0 = logit(s), so

    g_0 = sigma(logit(s)) = s        exactly

and therefore d = g_final - s. On the 34 plateau bands s = 1 and the trained
gate stays at 1, so

    d = 0 on the plateau, in every seed, BY CONSTRUCTION

Those 34 bands -- 12.1% of 281 -- agree trivially between any two seeds, and
that agreement enters rho(d). This is not the tie-breaking artifact: midranks
are deterministic, no sort decides anything, and the contribution is 12% rather
than 100%. But it is not nothing either, and "unaffected" is a stronger claim
than the program has earned.

So: recompute the displacement reproducibility over ALL bands and over the
NON-PLATEAU bands only. If the two agree, the control is independent of the
plateau and Section 9 can say so. If dropping 34 bands moves it materially,
Section 9 has to report the number with the qualification.

WHAT THIS IS NOT
----------------
This is NOT a recomputation of the published 0.9462. That figure comes from the
accepted study's own NIR run, which is not in this repository. These are the
inherited pgsg_1 R2 vectors -- same dataset, same prior, same initialisation
regime, ten seeds per training size. They test whether the plateau inflates a
displacement correlation in this regime. A result here constrains what we may
claim in general; it does not restate the published number.

Both Pearson and Spearman are reported because the published figure's
definition is not recorded in this repository, and the plateau acts differently
on the two: it is a block of identical values for Pearson and a block of equal
midranks for Spearman.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/09_controle_deslocamento.py --dir data/processed/gates_r2
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np

SEP = "=" * 78


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.std() < 1e-15 or b.std() < 1e-15:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman with midranks for ties -- deterministic, no sort arbitrariness."""
    from scipy.stats import rankdata
    return pearson(rankdata(a), rankdata(b))


def pares(mat: np.ndarray, f) -> tuple[float, float]:
    v = [f(mat[i], mat[j])
         for i, j in itertools.combinations(range(len(mat)), 2)]
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if v.size == 0:
        return float("nan"), float("nan")
    return float(v.mean()), float(v.std(ddof=1) if v.size > 1 else 0.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/processed/gates_r2")
    a = ap.parse_args()

    d = Path(a.dir).expanduser()
    arquivos = sorted(d.glob("gates_n*.npz"))
    if not arquivos:
        raise SystemExit(f"no gates_n*.npz in {d}")

    head("Displacement reproducibility, all bands against non-plateau only")
    print("d = g_final - g_0.  Under prior-init g_0 = sigma(logit(s)) = s, so")
    print("d = g_final - prior.  Under theta_0 = 0, g_0 = sigma(0) = 0.5.")
    print()
    print(f"{'file':<16}{'arm':<12}{'bands':<8}"
          f"{'Pearson':>18}{'Spearman':>18}")
    print("-" * 78)

    resumo: dict[tuple[str, str], float] = {}
    for p in arquivos:
        z = np.load(p, allow_pickle=False)
        if "prior" not in z.files:
            print(f"{p.name:<16}no prior stored, skipped")
            continue
        prior = np.asarray(z["prior"], float)
        plato = np.flatnonzero(prior >= prior.max() - 1e-9)
        fora = np.setdiff1d(np.arange(len(prior)), plato)

        for arm, g0 in (("gates_lit", prior), ("gates_rand", 0.5)):
            if arm not in z.files:
                continue
            g_ = np.atleast_2d(np.asarray(z[arm], float))
            desl = g_ - g0
            for nome, idx in (("all 281", np.arange(len(prior))),
                              (f"non-pl {len(fora)}", fora)):
                mp, sp = pares(desl[:, idx], pearson)
                ms, ss = pares(desl[:, idx], spearman)
                print(f"{p.name:<16}{arm:<12}{nome:<8}"
                      f"{mp:>10.4f} +-{sp:>6.4f}{ms:>10.4f} +-{ss:>6.4f}")
                resumo[(p.name, arm, nome)] = (mp, ms)
            # Three properties, kept apart because only the first was ever
            # measured and the text used to conflate them:
            #   (1) within a run, are the 34 plateau gate values equal?
            #   (2) across runs, is that value the SAME?
            #   (3) how far has the gate moved from the prior there?
            # check_gates_r2 measures (1) per row and never compares rows.
            # (2) is what makes the plateau contribute trivial agreement to
            # rho(d), and nothing in this programme measured it until now.
            # view(np.int64) compares bit patterns, which presupposes the
            # array really is float64. carregar() casts with float(), but an
            # assumption worth stating is worth checking.
            if g_.dtype != np.float64:
                raise SystemExit(
                    f"{p.name}/{arm}: dtype is {g_.dtype}, not float64, so the "
                    f"bit comparison below would compare the wrong width. "
                    f"Resolve this rather than silently reinterpreting.")
            p1_valor, p1_bits, c_r = [], [], []
            for g in g_:
                v = g[plato]
                # value equality on the stored doubles, and bit equality on
                # their representations. A 0.0 obtained by subtraction is not
                # by itself evidence of bit-identical storage, which is the
                # distinction the author asked for on 2026-10-26.
                p1_valor.append(np.unique(v).size == 1)
                p1_bits.append(np.unique(v.view(np.int64)).size == 1)
                c_r.append(float(v[0]) if p1_valor[-1] else float("nan"))
            todas_p1 = all(p1_valor)
            z_plato = float(np.abs(desl[:, plato]).max())
            print(f"{'':16}{'':12}P1 value-equal in {sum(p1_valor)}/{len(g_)} "
                  f"runs, bit-equal in {sum(p1_bits)}/{len(g_)};  max |d| "
                  f"{z_plato:.3e}")
            # Resolution of these measurements, at the VALUES OBSERVED and
            # not at 1.0. A gate is sigma(theta) < 1, so the plateau sits in
            # the binade [0.5, 1.0), where the single-precision spacing is
            # 2**-24. The spacing 2**-23 applies ABOVE 1.0: 1.0 is a power of
            # two and lies on the boundary between two spacing regions. An
            # earlier version of this script used 2**-23 and reported half the
            # number of steps.
            #
            # Spacing is a LOCAL property, so it is read at both ends of the
            # observed range. If the plateau values straddle a binade boundary
            # there is no single resolution to express P2 in, and the step
            # count is withheld rather than read at one end and applied to the
            # whole range.
            lo = float(np.abs(g_[:, plato]).min())
            hi = float(np.abs(g_[:, plato]).max())
            ulp_lo = float(np.spacing(np.float32(lo)))
            ulp_hi = float(np.spacing(np.float32(hi)))
            ULP32 = ulp_hi if ulp_lo == ulp_hi else float("nan")
            exato32 = bool(np.array_equal(
                g_[:, plato], g_[:, plato].astype(np.float32).astype(np.float64)))
            print(f"{'':16}{'':12}plateau values exactly representable in "
                  f"float32: {exato32};  single-precision spacing over "
                  f"[{lo:.9f}, {hi:.9f}] = {ulp_lo:.6e}"
                  + ("" if ulp_lo == ulp_hi else
                     f" at the low end and {ulp_hi:.6e} at the high end "
                     f"-- the values straddle a binade boundary, so there is "
                     f"no single resolution and no step count is reported"))
            if exato32:
                print(f"{'':16}{'':12}  NOTE: exact representability shows the "
                      f"stored float64 values lie on the float32 grid. It "
                      f"does NOT show they were computed in single precision "
                      f"-- rounding, an explicit cast or a quantisation step "
                      f"before storage would leave the same trace. Confirming "
                      f"provenance needs the dtypes used in training, export "
                      f"and loading.")
            if todas_p1:
                # A_inter over the COMMON plateau value per run, not over a
                # mean: a mean would hide within-run variation whenever P1
                # fails, which is exactly when the quantity is meaningless.
                A = float(np.ptp(np.asarray(c_r)))
                mult = A / ULP32
                print(f"{'':16}{'':12}P2 across-run amplitude of the common "
                      f"level: {A:.6e}"
                      + ("   (exactly equal)" if A == 0.0 else
                         "   [step count withheld: no single resolution]"
                         if not np.isfinite(mult) else
                         f"   = {mult:.2f} steps of {ULP32:.6e}"
                         + ("  [integer multiple]"
                            if abs(mult - round(mult)) < 1e-6 else "")))
            else:
                ruins = [i for i, ok in enumerate(p1_valor) if not ok]
                print(f"{'':16}{'':12}P2 NOT COMPUTED: P1 fails in run(s) "
                      f"{ruins}, so the plateau has no single value to compare "
                      f"across runs. Reporting the condition instead of "
                      f"assigning one.")
        print()

    head("Reading")
    print("If 'all 281' and 'non-pl' agree closely in both columns, the")
    print("displacement control does not depend on the prior's plateau, and")
    print("Section 9 may state its immunity without qualification.")
    print()
    print("If dropping the 34 plateau bands lowers the figure materially, then")
    print("part of the published displacement reproducibility is the trivial")
    print("agreement of 34 bands held at d = 0 by the initialisation. That is")
    print("NOT the tie-breaking artifact of findings/F002 -- no selection and")
    print("no arbitrary order are involved, and midranks are deterministic --")
    print("but it is a dependence on the plateau, and Section 9 must report it")
    print("rather than claim the control is unaffected.")
    print()
    print("Either way this constrains only what we CLAIM. It does not restate")
    print("the published 0.9462, which was measured on data not in this repo.")
    print()
    print("max |d| on the plateau should be ~0 under prior-init, which is the")
    print("premise of the whole question. If it is not, the premise is wrong")
    print("and the rest of this output needs rereading before it is used.")


if __name__ == "__main__":
    main()
