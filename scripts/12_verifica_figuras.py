#!/usr/bin/env python
"""Do the submitted figure files reproduce from the versioned code and data?

WHY
---
`scripts/10_figuras.py` draws the five figures from the data, and the script is
versioned. That documents their ORIGIN. It does not establish that they still
reproduce: an input may have moved, the script may fail part way, a library may
have changed, or the committed PDF may predate the last edit to the code that
draws it. Reproducibility of a procedure and conformity of a submitted file are
two different claims, and only the second is what a reader of the paper gets.

So this script does three things, and reports them separately:

  1. INPUTS.    For each figure, are the files it needs reachable? A figure
                whose inputs are absent is reported as NOT VERIFIABLE here.
                It is never reported as verified, and never as wrong.
  2. EXECUTION. Does 10_figuras.py run to completion, writing into a scratch
                directory? `paper/figuras` is never written to by this script.
  3. CONTENT.   Does each regenerated PDF show the same picture as the
                committed one? Compared by rasterising both and differencing
                the pixels, because matplotlib stamps a creation date into the
                PDF and byte equality therefore fails on identical pictures.

WHAT A PASS DOES AND DOES NOT MEAN
----------------------------------
A pixel match says the committed file shows what today's code and data draw.
It does not say the picture is correct, and a MISMATCH does not by itself mean
the data changed: a different matplotlib, freetype or numpy can move a glyph or
a tick by a pixel. The versions in use are printed so that a mismatch can be
read against them rather than guessed at. Interpreting one is a human
judgement, and this script refuses to make it.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/12_verifica_figuras.py
    python scripts/12_verifica_figuras.py \\
        --pgsg1-root ~/pgsg/pgsg_1 \\
        --pgsg2-root ~/pgsg/pgsg2-nir-raman-gating/src \\
        --raman results/raman_h12

`--pgsg2-root` is the directory that CONTAINS the `pgsg2` package -- that
repository's `src`, not the repository root. Passing the root fails, as it did
in the author's run of 2026-10-27; 10_figuras.py says so in its own error.

Rasterising needs pypdfium2 or a working poppler (pdftoppm). It is declared as
an optional extra, so `pip install -e '.[verify]'` installs it; a poppler
install satisfies it equally and cannot be declared in pyproject. With neither,
each figure is reported as NOT VERIFIABLE with the reason, because a byte
comparison would report every identical figure as different.

Exit status is 0 only when every figure was regenerated AND matched. Missing
inputs give a non-zero status too: "not verifiable" is not "fine".
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

SEP = "=" * 78

# Each figure, the committed file, and the inputs 10_figuras.py needs for it.
# Written out rather than inferred, so that an input moving is a visible
# failure instead of a silently skipped panel.
FIGURAS = {
    "fig1_prior_degrau.pdf": ("step prior and its levels",
                              ["gates dir"]),
    "fig2_colapso_por_desempate.pdf": ("tie-breaking collapse",
                                       ["gates dir"]),
    "fig3_resposta_ao_tamanho.pdf": ("response to training size",
                                     ["gates dir"]),
    "fig4_controle_raman.pdf": ("Raman control",
                                ["raman dir", "cells.json"]),
    "fig5_alinhamento_intra_nivel.pdf": ("within-level alignment",
                                         ["partition dirs p*"]),
}

DPI = 150
# A pixel differing by one or two levels out of 255 is anti-aliasing noise, not
# a different picture. The threshold is stated here rather than buried.
TOL_NIVEL = 2


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


class SemRasterizador(RuntimeError):
    """No working renderer. Reported per figure, never as a traceback."""


def _raster_poppler(pdf: Path, dpi: int, destino: Path) -> list[np.ndarray]:
    # The directory must exist before pdftoppm writes into it. It did not, in
    # the author's run of 2026-10-27, and pdftoppm exited 1 while the script
    # reported a CalledProcessError traceback instead of a verdict.
    destino.mkdir(parents=True, exist_ok=True)
    base = destino / pdf.stem
    r = subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf),
                        str(base)], capture_output=True, text=True)
    saidas = sorted(destino.glob(f"{pdf.stem}-*.png"))
    if r.returncode != 0 or not saidas:
        raise SemRasterizador(
            f"pdftoppm exited {r.returncode} on {pdf.name} and wrote "
            f"{len(saidas)} page(s). "
            + (r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")
            + "  Install pypdfium2 (pip install pypdfium2) or a working "
              "poppler-utils.")
    import matplotlib.image as mpimg
    return [np.asarray(mpimg.imread(p) * 255, dtype=np.int16) for p in saidas]


def paginas_de(pdf: Path, dpi: int, destino: Path) -> tuple[list, str]:
    try:
        import pypdfium2 as pdfium
    except ImportError:
        if shutil.which("pdftoppm") is None:
            raise SemRasterizador(
                "neither pypdfium2 nor pdftoppm is available. Install one of "
                "them (pip install pypdfium2) rather than falling back to a "
                "byte comparison, which fails on identical pictures because "
                "matplotlib stamps a creation date into every PDF.")
        return _raster_poppler(pdf, dpi, destino), "poppler/pdftoppm"
    doc = pdfium.PdfDocument(str(pdf))
    paginas = [np.asarray(doc[i].render(scale=dpi / 72.0).to_numpy(),
                          dtype=np.int16) for i in range(len(doc))]
    # pypdfium2 5.x exposes no __version__ attribute, so the old getattr
    # printed "pypdfium2 ?" -- a provenance field reporting that it does not
    # know, in a script whose purpose is provenance. The distribution
    # metadata has it. Author's run, 2026-10-27.
    try:
        from importlib.metadata import version
        v = version("pypdfium2")
    except Exception:
        v = getattr(pdfium, "__version__", "version unknown")
    return paginas, f"pypdfium2 {v}"


def comparar(a: Path, b: Path, dpi: int, destino: Path) -> dict:
    pa, motor = paginas_de(a, dpi, destino / "a")
    pb, _ = paginas_de(b, dpi, destino / "b")
    r = {"renderer": motor, "pages_a": len(pa), "pages_b": len(pb)}
    if len(pa) != len(pb):
        r["verdict"] = "DIFFERS (page count)"
        return r
    piores, fracoes = [], []
    for x, y in zip(pa, pb):
        if x.shape != y.shape:
            r["verdict"] = f"DIFFERS (size {x.shape} vs {y.shape})"
            return r
        d = np.abs(x - y)
        piores.append(int(d.max()))
        fracoes.append(float((d > TOL_NIVEL).mean()))
    r["max_abs_diff"] = max(piores)
    r["frac_over_tol"] = max(fracoes)
    r["verdict"] = ("IDENTICAL" if max(piores) == 0 else
                    "MATCHES (within anti-aliasing tolerance)"
                    if max(fracoes) == 0.0 else "DIFFERS")
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/processed/gates_r2")
    ap.add_argument("--results", default="results")
    ap.add_argument("--raman", default="results/raman_h12")
    ap.add_argument("--committed", default="paper/figuras")
    ap.add_argument("--pgsg1-root", default="")
    ap.add_argument("--pgsg2-root", default="")
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--keep", default="",
                    help="directory to keep the regenerated PDFs in")
    a = ap.parse_args()

    head("Figure reproduction check")
    import matplotlib
    import scipy
    print(f"numpy {np.__version__}   scipy {scipy.__version__}   "
          f"matplotlib {matplotlib.__version__}   python "
          f"{sys.version.split()[0]}")
    print("A mismatch can come from these versions as easily as from the "
          "data.\nThis script reports the difference and does not diagnose "
          "it.")

    comitado = Path(a.committed).expanduser()
    gates = Path(a.dir).expanduser()
    raman = Path(a.raman).expanduser()
    resultados = Path(a.results).expanduser()

    disponivel = {
        "gates dir": gates.is_dir() and any(gates.glob("gates_n*.npz")),
        "raman dir": raman.is_dir(),
        "cells.json": (raman / "cells.json").is_file(),
        "partition dirs p*": bool(list(resultados.glob("p*"))),
    }
    head("1. Inputs")
    for k, ok in disponivel.items():
        alvo = {"gates dir": gates, "raman dir": raman,
                "cells.json": raman / "cells.json",
                "partition dirs p*": f"{resultados}/p*"}[k]
        print(f"  {'present' if ok else 'MISSING':<8}  {k:<20}  {alvo}")
    if a.pgsg1_root or a.pgsg2_root:
        print(f"  pgsg1-root={a.pgsg1_root or '(unset)'}   "
              f"pgsg2-root={a.pgsg2_root or '(unset)'}")
    else:
        print("  pgsg1-root and pgsg2-root unset: Figure 1's reconstructed "
              "axis and\n  Figure 4's Raman prior fall back to whatever "
              "10_figuras.py does without them.")

    naoverificavel = {f: [n for n in req if not disponivel.get(n, False)]
                      for f, (_, req) in FIGURAS.items()}

    head("2. Execution")
    tmp = Path(a.keep).expanduser() if a.keep else Path(
        tempfile.mkdtemp(prefix="fig_check_"))
    tmp.mkdir(parents=True, exist_ok=True)
    saida = tmp / "regenerated"
    saida.mkdir(exist_ok=True)
    cmd = [sys.executable, "scripts/10_figuras.py", "--dir", str(gates),
           "--results", str(resultados), "--raman", str(raman),
           "--out", str(saida)]
    if a.pgsg1_root:
        cmd += ["--pgsg1-root", a.pgsg1_root]
    if a.pgsg2_root:
        cmd += ["--pgsg2-root", a.pgsg2_root]
    print("  " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"  exit status {r.returncode}")
    if r.returncode != 0:
        print("  --- stderr, last 20 lines ---")
        for linha in r.stderr.strip().splitlines()[-20:]:
            print("  " + linha)
        print("\n  10_figuras.py did not run to completion, so NOTHING that "
              "follows could be a\n  verification of the committed figures. "
              "This script stops here rather than\n  comparing whatever "
              "partial output happens to be on disk: a comparison run\n  "
              "against an incomplete regeneration is worse than no "
              "comparison, because\n  it looks like one.")
        sys.exit(1)

    head("3. Content, regenerated against committed")
    print(f"  rasterised at {a.dpi} dpi; a pixel differing by at most "
          f"{TOL_NIVEL}/255 is\n  treated as anti-aliasing and not as a "
          f"different picture")
    print()
    falhas, verificadas = [], 0
    for nome, (rotulo, _) in FIGURAS.items():
        alvo, novo = comitado / nome, saida / nome
        faltando = naoverificavel[nome]
        if not alvo.is_file():
            print(f"  {'NOT COMMITTED':<14}  {nome}")
            falhas.append(nome)
            continue
        if not novo.is_file():
            razao = (f"inputs missing: {', '.join(faltando)}" if faltando
                     else "not produced by this run")
            print(f"  {'NOT VERIFIABLE':<14}  {nome:<34}  {razao}")
            falhas.append(nome)
            continue
        try:
            c = comparar(alvo, novo, a.dpi, tmp)
        except SemRasterizador as e:
            print(f"  {'NOT VERIFIABLE':<14}  {nome:<34}  cannot rasterise")
            print(f"  {'':14}  {'':34}  {e}")
            falhas.append(nome)
            continue
        marca = "OK" if c["verdict"].startswith(("IDENTICAL", "MATCHES")) \
            else "FAIL"
        if marca == "OK":
            verificadas += 1
        else:
            falhas.append(nome)
        extra = (f"max|diff| {c['max_abs_diff']}, "
                 f"{c['frac_over_tol']*100:.4f}% of pixels over tolerance"
                 if "max_abs_diff" in c else "")
        print(f"  {marca:<14}  {nome:<34}  {c['verdict']}")
        if extra:
            print(f"  {'':14}  {'':34}  {extra}  [{c['renderer']}]")
        if faltando:
            print(f"  {'':14}  {'':34}  NOTE: regenerated despite missing "
                  f"{', '.join(faltando)} -- check what 10_figuras.py drew "
                  f"instead")

    head("Reading")
    print(f"  {verificadas} of {len(FIGURAS)} figures regenerated and matched.")
    if not a.keep:
        print(f"  regenerated files are in {saida} (temporary; pass --keep "
              f"DIR to keep them)")
    if falhas:
        print("  outstanding: " + ", ".join(falhas))
        print("\n  A figure listed here is NOT shown to be wrong. It is shown "
              "to be\n  unverified, which is a different and weaker "
              "statement -- and the one\n  that has to be resolved before the "
              "file is submitted as the paper's.")
    else:
        print("  Every committed figure reproduces from the versioned code "
              "and data at\n  these library versions. That is what this "
              "check can establish; it says\n  nothing about whether the "
              "figures are the right ones to publish.")
    sys.exit(0 if not falhas else 1)


if __name__ == "__main__":
    main()
