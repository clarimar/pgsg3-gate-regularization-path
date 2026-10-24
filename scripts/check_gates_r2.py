#!/usr/bin/env python
"""Are the inherited pgsg_1 R2 gate vectors tied in the prior's plateau?

WHY
---
`docs/adr/ADR-0001-escopo-e-datasets.md` decision 6 records, as pgsg_3's
established starting point, gate vectors from pgsg_1's R2 revision under two
initialisations:

    prior de literatura   rho(gate,prior) 0,9987--1,0000   Jaccard 0,945--0,987
    nao informada         rho 0,025--0,280                 Jaccard 0,090--0,566

The first row is the prior-in-initialisation regime: the same one where
findings/F002 showed the published NIR Jaccard of 0.9418 to be `np.argsort`
tie order over 34 bit-identical plateau values, collapsing to chance (0.7005)
when the ties are broken at random.

If those inherited vectors are tied the same way, the Jaccard column of that
table is the same artifact, and pgsg_3 cites it as its own starting point.
There is no published paper at stake -- that manuscript was rejected and will
not be resubmitted -- but the internal inconsistency has to be known before
the pgsg_3 text is written, not after a reviewer asks.

This script trains nothing and writes nothing. It reads the stored vectors,
rebuilds the literature prior from the wavelength axis, and reports ties.

USAGE
-----
    cd ~/pgsg/pgsg_3
    export PGSG1_ROOT=~/Dropbox/pgsg/pgsg_1/src
    python check_gates_r2.py --dir data/processed/gates_r2

If the layout differs, point --dir at whatever directory holds the vectors;
the script reports what it finds before interpreting anything.
"""

from __future__ import annotations

import argparse
import itertools
import os
import sys
from pathlib import Path

import numpy as np

SEP = "=" * 78


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def carregar(caminho: Path) -> dict[str, np.ndarray]:
    """Whatever this file holds, as named 1-D float arrays."""
    if caminho.suffix == ".npz":
        z = np.load(caminho, allow_pickle=False)
        return {k: np.asarray(z[k], float) for k in z.files
                if np.asarray(z[k]).ndim in (1, 2)}
    if caminho.suffix == ".npy":
        a = np.asarray(np.load(caminho, allow_pickle=False), float)
        return {caminho.stem: a}
    if caminho.suffix in (".csv", ".txt"):
        try:
            a = np.loadtxt(caminho, delimiter=",")
        except ValueError:
            a = np.loadtxt(caminho)
        return {caminho.stem: np.asarray(a, float)}
    return {}


def jaccard_medio(gates: list[np.ndarray], q: int) -> float:
    tops = [set(np.argsort(g)[::-1][:q].tolist()) for g in gates]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


def jaccard_sorteando_empates(gates: list[np.ndarray], q: int,
                              draws: int = 200, seed: int = 0) -> tuple:
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        tops = []
        for g in gates:
            chave = rng.random(len(g))
            tops.append(set(np.lexsort((chave, -g))[:q].tolist()))
        vals.append(np.mean([len(a & b) / len(a | b)
                             for a, b in itertools.combinations(tops, 2)]))
    v = np.asarray(vals)
    return float(v.mean()), float(v.std(ddof=1) if len(v) > 1 else 0.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/processed/gates_r2")
    ap.add_argument("--pgsg1-root", default=os.environ.get("PGSG1_ROOT", ""))
    ap.add_argument("--decil", type=float, default=0.10)
    ap.add_argument("--q", type=int, default=None,
                    help="top-q explicito. Sem isto, usa ceil(decil*p). "
                         "A truncagem int(decil*p) da 28 em p=281 e e a "
                         "convencao da ablacao H4 do pgsg_2; gate_metrics.csv "
                         "e o pgsg_3 usam ceil, que da 29. Protocolos "
                         "diferentes nao se misturam.")
    a = ap.parse_args()

    d = Path(a.dir).expanduser()
    if not d.is_dir():
        raise SystemExit(f"{d} is not a directory. Point --dir at the stored "
                         f"R2 gate vectors.")

    arquivos = sorted(p for p in d.rglob("*")
                      if p.suffix in (".npz", ".npy", ".csv", ".txt"))
    head(f"What is in {d}")
    if not arquivos:
        raise SystemExit("no .npz/.npy/.csv/.txt found. Nothing to check.")
    achados = {}
    for p in arquivos:
        try:
            conteudo = carregar(p)
        except Exception as e:                                # noqa: BLE001
            print(f"  {p.relative_to(d)}   unreadable: {e}")
            continue
        achados[p] = conteudo
        for k, v in conteudo.items():
            print(f"  {str(p.relative_to(d)):<44} {k:<22} {str(v.shape):<12} "
                  f"{v.dtype}")

    # ----------------------------------------------------- the prior's plateau
    prior = None
    if a.pgsg1_root:
        raiz = str(Path(a.pgsg1_root).expanduser())
        if raiz not in sys.path:
            sys.path.insert(0, raiz)
    for base in (Path.cwd() / "src" / "pgsg_3" / "m_model",
                 Path.cwd() / "vendor" / "pgsg_1"):
        if base.is_dir() and str(base) not in sys.path:
            sys.path.insert(0, str(base))
    wl = None
    for conteudo in achados.values():
        for k, v in conteudo.items():
            if "wavelength" in k.lower() or "wl" == k.lower():
                wl = v
    try:
        from pgsg_v2 import make_literature_prior
        if wl is not None:
            prior = np.asarray(make_literature_prior(wl), float)
    except Exception as e:                                    # noqa: BLE001
        print(f"\n  could not rebuild the prior ({e}).")

    head("Ties inside the prior's plateau")
    if prior is None:
        print("The wavelength axis or make_literature_prior was not available,")
        print("so the plateau cannot be located from the prior. Falling back to")
        print("reporting ties among each vector's own maximum, which is the")
        print("same question ONLY when the gate is pinned at the prior's")
        print("ceiling. Re-run with PGSG1_ROOT exported and from inside the")
        print("pgsg_3 checkout so the real prior is used instead.\n")
    else:
        niveis, contagens = np.unique(prior, return_counts=True)
        plato = np.flatnonzero(prior >= prior.max() - 1e-9)
        print("prior levels : "
              + "  ".join(f"{v:.4g} x{c}" for v, c in zip(niveis, contagens)))
        print(f"plateau      : {len(plato)} bands\n")

    for p, conteudo in achados.items():
        for k, v in conteudo.items():
            mat = v if v.ndim == 2 else v[None, :]
            if prior is not None and mat.shape[1] != len(prior):
                continue
            if mat.shape[1] < 50:
                continue
            # a gate lives in (0,1); anything else here is an axis or a
            # metric stored alongside, and reporting s(1-s) for it is noise
            if mat.min() < -1e-9 or mat.max() > 1.0 + 1e-9:
                print(f"  {str(p.relative_to(d)):<36} {k:<18} skipped: values "
                      f"outside [0,1], not a gate")
                continue
            q = (a.q if a.q
                 else max(1, int(np.ceil(mat.shape[1] * a.decil))))
            idx = (plato if prior is not None
                   else np.flatnonzero(mat[0] >= mat[0].max() - 1e-9))
            if len(idx) < 3:
                print(f"  {str(p.relative_to(d)):<36} {k:<18} skipped: the "
                      f"tie group at the maximum has {len(idx)} band(s), so "
                      f"there is no tie to examine")
                continue
            distintos = [len(np.unique(g[idx])) for g in mat]
            espalh = [float(g[idx].max() - g[idx].min()) for g in mat]
            sat = [float((g[idx] * (1 - g[idx])).mean()) for g in mat]
            dentro = [len(set(np.argsort(g)[::-1][:q].tolist())
                          & set(idx.tolist())) / q for g in mat]
            print(f"  {str(p.relative_to(d)):<36} {k:<18} rows={len(mat):<3} "
                  f"plateau distinct {min(distintos)}..{max(distintos)} of "
                  f"{len(idx)}")
            print(f"  {'':36} {'':18} spread {min(espalh):.1e}..{max(espalh):.1e}"
                  f"   mean s(1-s) {min(sat):.1e}..{max(sat):.1e}")
            print(f"  {'':36} {'':18} decile inside plateau "
                  f"{min(dentro):.3f}..{max(dentro):.3f}   q={q}")
            if len(mat) >= 2:
                ji = jaccard_medio(list(mat), q)
                jr, sd = jaccard_sorteando_empates(list(mat), q)
                chance = (q / (2 * len(idx) - q)
                          if len(idx) >= q else float("nan"))
                print(f"  {'':36} {'':18} Jaccard INDEX {ji:.4f}   "
                      f"RANDOM {jr:.4f} +- {sd:.4f}   chance {chance:.4f}")
            print()

    head("Reading")
    print("A plateau with 1 distinct value and spread 0.0e+00 means the stored")
    print("gate carries no ordering there, so the top decile is whatever")
    print("np.argsort's partition yields. If INDEX is far above RANDOM, the")
    print("Jaccard column of ADR-0001 decision 6 is the artifact of")
    print("findings/F002 and not a measure of band selection.")
    print()
    print("No published paper depends on this: that manuscript was rejected")
    print("and will not be resubmitted. What depends on it is pgsg_3's own")
    print("statement of its starting point, which has to be corrected in the")
    print("ADR and in the manuscript if this comes back tied.")
    print()
    print("The rho column is NOT affected either way: rho(gate,prior) uses the")
    print("values, not their order, and 0.9987 is a real measurement.")
    print()
    print("DECILE CONVENTION. q defaults to ceil(0.10*p) = 29 at p=281, which")
    print("is what gate_metrics.csv records and what pgsg_3 uses. The pgsg_2")
    print("H4 ablation uses floor division, q = 28. The two give different")
    print("numbers (chance 0.7436 against 0.7000) and must be reported per")
    print("protocol, never mixed. Pass --q to pin one explicitly.")


if __name__ == "__main__":
    main()
