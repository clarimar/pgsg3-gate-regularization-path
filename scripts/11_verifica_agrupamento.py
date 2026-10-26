#!/usr/bin/env python
"""Is the fruit grouping sound, and does any fruit straddle the split?

WHY
---
`src/pgsg_3/g_ingest/grouped.py` builds the grouping variable like this:

    Fruit id per spectrum: runs of consecutive rows with identical metadata.
    Mango DMC v3 has no fruit-ID column. Replicate spectra of one fruit are
    consecutive rows sharing every metadata field and the dry-matter value.

So the fruit identifier is INFERRED, not read. `check_alignment` verifies only
that the CSV and the loader agree on row order, by comparing the DM column; it
does not verify that replicates are consecutive, nor that groups have the
expected size. `group_split` then splits whole GROUPS, so no group straddles
the train/test boundary -- but if one fruit maps to more than one group,
because its replicate rows are not adjacent, that fruit can appear on both
sides. That would be leakage, and it is a different and worse problem than the
between-partition dependence of findings/F003.

This script does not argue about it. It measures three things:

  1. the group-size distribution, against the recorded structure of 725 fruits
     of which 723 were measured twice;
  2. whether any metadata+DM key appears in more than one group, which is the
     signature of a fruit split across groups;
  3. for every split seed actually used, whether any metadata+DM key appears
     in BOTH the training and the test side. This is the decisive test: it
     holds whatever the group ids are, because it asks the question directly.

It trains nothing and writes nothing.

WHAT CHECK 3 DOES AND DOES NOT ESTABLISH
----------------------------------------
Check 3 establishes a verifiable property: no metadata+DM key appears in both
the training and the test side. It does NOT, on its own, establish that no
physical fruit does. That step needs one further hypothesis -- that every
measurement of one fruit carries exactly the same metadata+DM key -- and that
hypothesis is the basis of the fruit-identification procedure itself. The
check is therefore circular with respect to it, and the CSV holds no fruit-ID
column with which to break the circle. Three cases have to be kept apart:

  same fruit, same key          check 3 detects a straddling split
  same fruit, different keys    check 3 may miss the leakage
  different fruits, same key    check 3 may flag a collision that is not one

So check 3 clean is strong evidence and not a proof. What it proves is that
the splits respect the observable key structure.

THREE STATES
------------
A  checks 1, 2 and 3 pass. The grouping is consistent with the dataset's
   observable assumptions. The work may proceed, declaring that fruit
   identity was INFERRED and not supplied.
B  check 3 passes, 1 or 2 fails. No leakage was detected by the observable
   keys in the splits examined, but the grouping does not reproduce the
   recorded structure. That inconsistency must be investigated before the
   per-fruit separation is considered validated. This is NOT automatically
   safe, and an earlier version of this script said it was.
C  check 3 fails. Keys are shared between training and test. Suspend the
   out-of-sample claims resting on the affected splits, and then work out
   which results actually depend on the compromised split before deciding
   what to rerun. A leakage problem does not touch every result equally, and
   the section a result appears in is the wrong unit of decision:
     - results that rest on held-out evaluation are directly affected;
     - results about stability across initialisations are computed on the
       training side and are affected only through what was trained on;
     - results that describe properties of the prior or of the gate -- level
       counts, plateau size, tie structure, within-level correlations against
       a reference recomputed per partition -- may be unaffected entirely.
   Identify the dependence, not the heading.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/11_verifica_agrupamento.py --csv <path to the Mango CSV>

The CSV path defaults to the same discovery the sweep uses.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

SEP = "=" * 78
# SEASON and TEST_FRACTION are NOT redefined here. The verifier must use the
# experiments' own configuration, because the same seed does not give the same
# partition when the season filter, the test fraction, the row order or the
# group_split implementation differ. They are imported from the sweep script
# at run time and the values are printed, so a divergence is visible rather
# than silent. An earlier version of this file duplicated both as literals.
# Every split seed this programme actually uses, read off the run commands
# recorded in the pre-registrations and finding notes:
#   0..4    the prior controls of findings/F002 (ctl_part*, ctl_blocks_part*,
#           ctl_shuffled_part*)
#   5..9    findings/F003
#   10..14  findings/F006, the replication partitions
#   42      the argument default of 02_lambda_sweep_controlled.py
# An earlier version of this script checked only 5..14 and the result was
# reported as though it covered the programme. It did not.
SEEDS_USADAS = tuple(range(0, 15)) + (42,)
FRUTOS_ESPERADOS = 725
MEDIDOS_DUAS_VEZES = 723


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def constantes_do_sweep(caminho: Path) -> dict:
    """SEASON and TEST_FRACTION as the sweep script declares them.

    Read by parsing, not by import: importing 02 pulls in torch. If either
    name is missing, or is no longer a plain literal, this raises rather than
    falling back on a copied value -- a silent copy is how a verifier ends up
    checking a configuration the experiments do not use.
    """
    import ast as _ast
    arvore = _ast.parse(caminho.read_text())
    saida: dict[str, object] = {}
    for no in arvore.body:
        if isinstance(no, _ast.Assign) and len(no.targets) == 1:
            alvo = no.targets[0]
            if isinstance(alvo, _ast.Name) and alvo.id in ("SEASON",
                                                           "TEST_FRACTION"):
                try:
                    saida[alvo.id] = _ast.literal_eval(no.value)
                except ValueError:
                    raise SystemExit(
                        f"{caminho.name}: {alvo.id} is no longer a literal, so "
                        f"this verifier cannot read the experiments' "
                        f"configuration without executing the module. Fix "
                        f"this rather than copying the value.") from None
    faltam = {"SEASON", "TEST_FRACTION"} - set(saida)
    if faltam:
        raise SystemExit(f"{caminho.name}: could not find {sorted(faltam)}. "
                         f"The verifier must not guess them.")
    return saida


def achar_csv_simples(root: Path):
    """The Mango CSV under the pgsg_1 tree, by name.

    The sweep's own achar_csv cannot be called without importing the module
    and therefore torch, so this does the one thing it needs to. Pass --csv
    and this is never used.
    """
    for pat in ("**/MangoDMC_NIR_Data_v3.csv", "**/*MangoDMC*v3*.csv",
                "**/*mango*v3*.csv"):
        for c in sorted(root.expanduser().glob(pat)):
            return c
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None)
    ap.add_argument("--pgsg1-root", default="~/Dropbox/pgsg/pgsg_1")
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS_USADAS))
    a = ap.parse_args()

    raiz = Path(__file__).resolve().parents[1]
    if str(raiz / "src") not in sys.path:
        sys.path.insert(0, str(raiz / "src"))
    from pgsg_3.g_ingest.grouped import (FRUIT_META, fruit_groups,  # noqa: E402
                                         group_split)

    # The experiments' own configuration, read from the sweep script WITHOUT
    # executing it: importing it pulls in torch, which a verification script
    # has no business requiring. Parsing the literals gives the same values
    # with no dependency, and raises if they are absent or no longer literals.
    cfg = constantes_do_sweep(raiz / "scripts" / "02_lambda_sweep_controlled.py")
    SEASON = int(cfg["SEASON"])
    TEST_FRACTION = float(cfg["TEST_FRACTION"])

    csv = a.csv
    if csv is None:
        csv = achar_csv_simples(Path(a.pgsg1_root).expanduser())
    if csv is None:
        raise SystemExit("Mango CSV not found; pass --csv explicitly.")
    csv = Path(csv).expanduser()

    import pandas as pd
    # FRUIT_META already ends with "DM", so the key IS metadata+DM and the
    # column must not be requested twice
    assert "DM" in FRUIT_META, "FRUIT_META no longer carries DM; the key below"
    df = pd.read_csv(csv, usecols=list(FRUIT_META))
    df = df[df["Season"] == SEASON].reset_index(drop=True)
    chave = df.astype(str).agg("|".join, axis=1).to_numpy()
    grupos = fruit_groups(csv, SEASON)

    head("What the grouping is built from")
    print(f"CSV            : {csv}")
    print(f"metadata fields: {list(FRUIT_META)}")
    print(f"season filter  : {SEASON}            <- read from "
          f"02_lambda_sweep_controlled.py, not copied")
    print(f"test fraction  : {TEST_FRACTION}          <- idem")
    print(f"grouping fn    : {fruit_groups.__module__}.fruit_groups")
    print(f"split fn       : {group_split.__module__}.group_split")
    print(f"season {SEASON} rows  : {len(df)}")
    print(f"groups found   : {len(np.unique(grupos))}")
    print()
    print("The fruit id is INFERRED from runs of consecutive identical")
    print("metadata, not read from a column. These checks test that.")

    # ------------------------------------------------- 1. group sizes
    head("1. Group-size distribution")
    tam, cont = np.unique(np.bincount(grupos), return_counts=True)
    for t_, c_ in zip(tam, cont):
        if t_ == 0:
            continue
        print(f"  groups of {t_:>2} spectra: {c_}")
    n_g = len(np.unique(grupos))
    dois = int(cont[tam == 2][0]) if (tam == 2).any() else 0
    um = int(cont[tam == 1][0]) if (tam == 1).any() else 0
    print()
    print(f"  recorded structure: {FRUTOS_ESPERADOS} fruits, "
          f"{MEDIDOS_DUAS_VEZES} measured twice")
    print(f"  that predicts     : {MEDIDOS_DUAS_VEZES} groups of 2 and "
          f"{FRUTOS_ESPERADOS - MEDIDOS_DUAS_VEZES} of 1, "
          f"{MEDIDOS_DUAS_VEZES * 2 + (FRUTOS_ESPERADOS - MEDIDOS_DUAS_VEZES)}"
          f" spectra")
    print(f"  measured          : {dois} of 2 and {um} of 1, "
          f"{len(df)} spectra, {n_g} groups")
    ok1 = (n_g == FRUTOS_ESPERADOS and dois == MEDIDOS_DUAS_VEZES)
    print(f"  -> {'MATCHES' if ok1 else 'DOES NOT MATCH the recorded structure'}")

    # --------------------------- 2. one key appearing in more than one group
    head("2. Does any fruit map to more than one group?")
    por_chave: dict[str, set] = {}
    for k, g in zip(chave, grupos):
        por_chave.setdefault(k, set()).add(int(g))
    partidas = {k: v for k, v in por_chave.items() if len(v) > 1}
    print(f"  distinct metadata+DM keys : {len(por_chave)}")
    print(f"  keys spanning >1 group    : {len(partidas)}")
    if partidas:
        print("  This is the signature of replicate rows that are NOT")
        print("  adjacent, so one fruit was counted as several. Examples:")
        for k, v in list(partidas.items())[:5]:
            print(f"    groups {sorted(v)}  key={k[:70]}")
    ok2 = not partidas
    print(f"  -> {'clean' if ok2 else 'IMPERFECT GROUPING'}")

    # ------------------------- 3. the decisive test: does a key straddle?
    head("3. Does any fruit appear on BOTH sides of a split?")
    print("  This holds whatever the group ids are: it asks the question")
    print("  directly, on the metadata+DM key.\n")
    sujo = []
    for seed in a.seeds:
        tr, te = group_split(grupos, TEST_FRACTION, seed)
        k_tr, k_te = set(chave[tr]), set(chave[te])
        comum = k_tr & k_te
        n_ftr, n_fte = len(k_tr), len(k_te)
        print(f"  seed {seed:>3}: train {len(tr):>5} spectra / {n_ftr:>4} keys   "
              f"test {len(te):>5} / {n_fte:>4}   shared keys: {len(comum)}"
              f"{'   <-- LEAKAGE' if comum else ''}")
        if comum:
            sujo.append((seed, sorted(comum)[:3]))
    ok3 = not sujo

    head("Reading")
    print(f"Seeds examined: {sorted(a.seeds)}")
    faltam = sorted(set(SEEDS_USADAS) - set(a.seeds))
    if faltam:
        print(f"NOT examined, though this programme uses them: {faltam}")
        print("The conclusion below is restricted to the seeds examined.")
    else:
        print("That is every split seed this programme is known to use "
              "(0..14 and the default 42).")
    print()
    if ok3:
        print("Check 3 is clean: in each split examined, no metadata+DM key")
        print("appears on both sides. The splits respect the observable key")
        print("structure.")
        print()
        print("This is strong evidence and not a proof of fruit-level")
        print("separation. Concluding that no physical fruit straddles a split")
        print("needs the further hypothesis that every measurement of one")
        print("fruit carries the same metadata+DM key -- which is the basis of")
        print("the identification procedure itself, so the check is circular")
        print("with respect to it. The CSV has no fruit-ID column to break")
        print("that circle, and this is a property of the source data, not of")
        print("the splitting procedure.")
    else:
        print("Check 3 is DIRTY. Some fruit appears in both training and test.")
        print("This is leakage, it is NOT the between-partition dependence of")
        print("findings/F003, and it is worse: the held-out performance of")
        print("every grouped run in this programme has to be revisited before")
        print("anything else is written. Affected seeds:")
        for seed, ex in sujo:
            print(f"  seed {seed}: e.g. {ex}")
    print()
    if ok1 and ok2 and ok3:
        print("STATE A. Checks 1 and 2 are clean too: the inferred grouping")
        print("reproduces the recorded structure exactly, so the observable")
        print("data are consistent with 725 fruits of which 723 were measured")
        print("twice. The work may proceed, declaring in the methods that")
        print("fruit identity was inferred and not supplied.")
    elif ok3:
        print("STATE B. Check 3 passes but check "
              f"{'1' if not ok1 else ''}{' and ' if not ok1 and not ok2 else ''}"
              f"{'2' if not ok2 else ''} does not. No leakage was detected by")
        print("the observable keys in the splits examined, but the grouping")
        print("does not reproduce the recorded structure. That inconsistency")
        print("must be investigated before the per-fruit separation is treated")
        print("as validated. Do NOT read this as safe.")
    else:
        print("STATE C. See above.")
    print()
    print("Either way this says nothing about the BETWEEN-partition")
    print("dependence: those ten splits share about 80% of their training")
    print("fruits by construction, which is a separate matter, already")
    print("measured, and recorded in findings/F003.")

    raise SystemExit(0 if ok3 else 2)


if __name__ == "__main__":
    main()
