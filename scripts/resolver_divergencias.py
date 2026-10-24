#!/usr/bin/env python
"""Resolve the two numeric discrepancies before the methods section is written.

Both are blocking per the review, and neither may go into the manuscript as a
known inconsistency.

(1) RAMAN SAMPLE COUNT. ADR-0001 of pgsg_2 declares 6,960 spectra; the run
    loaded 6,472. `RamanBioprocessSubstratesLoader.load` drops rows whose
    glucose target is NaN and records how many in
    `metadata["n_samples_dropped_missing_target"]`. If that equals 488 the two
    figures are compatible and the exclusion criterion is documented at source,
    not inferred. This reads the metadata instead of assuming it.

(2) JACCARD RANGE. ADR-0001 of pgsg_3, decision 6, states 0.945--0.987 for the
    literature arm; recomputing from the stored gates gave 0.9479--1.0000.
    `gate_metrics.csv` in the same directory carries the stored per-size
    values AND a `q` column, so the comparison can be made on the same
    protocol: same q, same decile definition, same tie rule. If their q differs
    from p // 10 the two ranges measure different things and both can be
    correct -- but then they must not be presented as the same experiment.

Writes nothing. Reads the loader metadata and the stored CSV.

USAGE
-----
    cd ~/pgsg/pgsg_3
    export PGSG1_ROOT=~/Dropbox/pgsg/pgsg_1/src
    python scripts/resolver_divergencias.py \
        --pgsg2-root ~/pgsg/pgsg2-nir-raman-gating/src \
        --gates-dir data/processed/gates_r2

Skip part 1 with --skip-raman if you would rather not re-download: the loader
metadata needs the dataset in cache.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import sys
from pathlib import Path

import numpy as np

SEP = "=" * 78
DECLARADO_ADR = 6960
ADR_JACCARD = (0.945, 0.987)


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}", flush=True)


def jaccard_medio(gates: list[np.ndarray], q: int) -> float:
    tops = [set(np.argsort(g)[::-1][:q].tolist()) for g in gates]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


# ------------------------------------------------------------------- part one

def contagem_raman(pgsg2_root: Path) -> None:
    head("(1) Raman sample count")
    p = str(pgsg2_root.resolve())
    if p not in sys.path:
        sys.path.insert(0, p)
    try:
        from pgsg2.ingestion.raman_bioprocess import (
            RamanBioprocessSubstratesLoader)
    except ModuleNotFoundError as e:
        print(f"could not import the loader ({e}).")
        print(f"--pgsg2-root must contain the `pgsg2` package, i.e. the repo's")
        print(f"`src`. given: {pgsg2_root.resolve()}")
        return

    ds = RamanBioprocessSubstratesLoader().load()
    descartados = ds.metadata.get("n_samples_dropped_missing_target")
    print(f"loaded n            : {ds.n_samples}")
    print(f"bands p             : {ds.n_bands}")
    print(f"dropped (NaN target): {descartados}")
    print(f"ADR-0001 declares   : {DECLARADO_ADR}")
    soma = (ds.n_samples + descartados) if descartados is not None else None
    print(f"loaded + dropped    : {soma}")
    print()
    if soma == DECLARADO_ADR:
        print("RECONCILED. The two figures are compatible: the loader drops")
        print("spectra whose glucose target is NaN, and the count is recorded")
        print("at source. The methods section states the declared total, the")
        print("exclusion criterion, and the analysed total.")
    elif descartados is None:
        print("the metadata key is absent -- this loader version does not")
        print("record the count. Reconcile by other means before writing.")
    else:
        print(f"NOT RECONCILED: {soma} != {DECLARADO_ADR}. Something other than")
        print("the missing-target filter accounts for the difference. Do not")
        print("write the methods section until this is explained.")


# ------------------------------------------------------------------- part two

def faixa_jaccard(gates_dir: Path) -> None:
    head("(2) Jaccard range: ADR-0001 decision 6 against recomputation")
    csv_path = gates_dir / "gate_metrics.csv"
    if not csv_path.is_file():
        print(f"{csv_path} not found; cannot compare on the same protocol.")
        return

    with csv_path.open() as f:
        linhas = list(csv.DictReader(f))
    if not linhas:
        print("gate_metrics.csv is empty.")
        return

    print("stored in gate_metrics.csv:\n")
    campos = linhas[0].keys()
    ql = [c for c in ("q", "k_lit") if c in campos]
    print(f"  {'n':>6} {'p':>6} " + " ".join(f"{c:>9}" for c in ql)
          + f" {'jaccard_lit':>12} {'jaccard_rand':>13}")
    armazenado = {}
    for r in linhas:
        n = int(float(r.get("n_actual", r.get("n", 0))))
        jl = float(r["jaccard_lit"])
        armazenado[n] = (jl, {c: r.get(c) for c in ql},
                         int(float(r.get("p", 0))))
        print(f"  {n:>6} {r.get('p', '?'):>6} "
              + " ".join(f"{r.get(c, '?'):>9}" for c in ql)
              + f" {jl:>12.4f} {float(r['jaccard_rand']):>13.4f}")

    jl_vals = [v[0] for v in armazenado.values()]
    print(f"\nstored range      : {min(jl_vals):.4f} -- {max(jl_vals):.4f}")
    print(f"ADR-0001 states   : {ADR_JACCARD[0]:.3f} -- {ADR_JACCARD[1]:.3f}")

    # recompute from the stored gates, at each q the file itself records and at
    # p // 10, so a q mismatch is visible instead of being absorbed
    print("\nrecomputed from the stored gate vectors:\n")
    print(f"  {'n':>6} {'q stored':>9} {'J at q stored':>14} "
          f"{'q=p//10':>8} {'J at p//10':>11} {'J at ceil':>10}")
    recalc = []
    for n in sorted(armazenado):
        f = gates_dir / f"gates_n{n}.npz"
        if not f.is_file():
            print(f"  {n:>6}   gates_n{n}.npz not found")
            continue
        z = np.load(f)
        g = [np.asarray(x, float) for x in z["gates_lit"]]
        p = len(g[0])
        q_st = armazenado[n][1].get("q") or armazenado[n][1].get("k_lit")
        q_st = int(float(q_st)) if q_st not in (None, "", "?") else None
        q_fl, q_ce = max(1, p // 10), int(np.ceil(0.10 * p))
        j_st = jaccard_medio(g, q_st) if q_st else float("nan")
        j_fl, j_ce = jaccard_medio(g, q_fl), jaccard_medio(g, q_ce)
        recalc.append((n, q_st, j_st, q_fl, j_fl, q_ce, j_ce))
        print(f"  {n:>6} {str(q_st):>9} {j_st:>14.4f} {q_fl:>8} "
              f"{j_fl:>11.4f} {j_ce:>10.4f}")

    if not recalc:
        return
    head("Reading")
    coincide = all(abs(r[2] - armazenado[r[0]][0]) < 5e-4 for r in recalc
                   if r[1])
    if coincide:
        # which of the three recomputed ranges does the ADR match?
        faixas = {
            "the file's own q": (min(r[2] for r in recalc if r[1]),
                                 max(r[2] for r in recalc if r[1])),
            "p // 10": (min(r[4] for r in recalc), max(r[4] for r in recalc)),
            "ceil(0.10 p)": (min(r[6] for r in recalc),
                             max(r[6] for r in recalc)),
        }
        casa = [k for k, (lo, hi) in faixas.items()
                if abs(lo - ADR_JACCARD[0]) < 5e-3
                and abs(hi - ADR_JACCARD[1]) < 5e-3]
        print("At the q the file itself records, the recomputation matches the")
        print("stored values.")
        print()
        if casa:
            print(f"And the ADR's range matches: {', '.join(casa)}.")
            print("So the ADR quoted the stored protocol and is CORRECT. Any")
            print("earlier 'discrepancy' came from a checker using a different")
            print("decile convention, not from the ADR. Nothing to correct")
            print("there; what must be corrected is whichever document reported")
            print("the mismatched convention as the data's own.")
        else:
            print("But the ADR's range matches none of the three. It was")
            print("quoted from a different subset or a different protocol, and")
            print("the two are not the same experiment. State one protocol in")
            print("the methods and correct the ADR by a dated note.")
    else:
        print("The recomputation does NOT match the stored values even at the")
        print("file's own q. The difference is not a decile convention, and the")
        print("methods section must wait until it is explained.")
    faixa = (min(r[2] for r in recalc if r[1]),
             max(r[2] for r in recalc if r[1]))
    print(f"\nrange at the file's own q : {faixa[0]:.4f} -- {faixa[1]:.4f}")
    print(f"range at p // 10          : {min(r[4] for r in recalc):.4f} -- "
          f"{max(r[4] for r in recalc):.4f}")
    print(f"range at ceil(0.10 p)     : {min(r[6] for r in recalc):.4f} -- "
          f"{max(r[6] for r in recalc):.4f}")
    print(f"ADR-0001                  : {ADR_JACCARD[0]:.3f} -- "
          f"{ADR_JACCARD[1]:.3f}")
    print()
    print("Whichever row the ADR matches is the protocol it used. Note that a")
    print("fully tied plateau makes all of these tie-order artefacts (F002,")
    print("F004): the point of this table is only to say which protocol the")
    print("ADR quoted, not to rehabilitate the number.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg2-root", default=None)
    ap.add_argument("--gates-dir", default="data/processed/gates_r2")
    ap.add_argument("--skip-raman", action="store_true")
    a = ap.parse_args()

    if not a.skip_raman:
        if not a.pgsg2_root:
            print("pass --pgsg2-root or --skip-raman")
        else:
            contagem_raman(Path(a.pgsg2_root).expanduser())
    faixa_jaccard(Path(a.gates_dir).expanduser())


if __name__ == "__main__":
    main()
