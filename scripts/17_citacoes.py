#!/usr/bin/env python3
"""Measure the citation state of the manuscript, and refuse to approve a
reference list that cannot be checked.

WHY THIS EXISTS
---------------
On 2026-10-29 the closing list said "check the references (brackets, LTWA)",
which presupposes references to check. A scan found none: no `[n]` marker, no
author-year citation, no `.bib` file, no `## References` block anywhere in
`paper/`. The gap was not a short list but the absence of the section, and the
wording of the item had hidden it.

WHAT IT CHECKS, AND WHAT IT DOES NOT
------------------------------------
Every check below is arithmetic on the text. None of them is an opinion about
whether a reference is the right one, and none of them can tell whether a
citation supports the sentence it is attached to. That is reading, and it stays
with the author.

  1. markers found in the manuscript text, by order of first appearance;
  2. every marker resolves to an entry in the reference list;
  3. every entry is cited at least once;
  4. the numbering follows first appearance, which the guide requires;
  5. no entry carrying `[FALTA:` sits in a list declared complete;
  6. the declared Status of `12-referencias.md` is reported, never guessed.

The reference file declares its own state on a `Status:` line. While that line
says INCOMPLETO this script reports and exits non-zero on request, and the
consolidator does not emit a references section at all: a partial list emitted
in silence is the failure this programme refuses.

Usage
-----
    python scripts/17_citacoes.py                 # report
    python scripts/17_citacoes.py --strict        # non-zero unless complete
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PAPER = RAIZ / "paper"
REFS = "12-referencias.md"
SEP = "=" * 78

# The drafts whose English prose is the manuscript text. Taken from the
# consolidator's ORDEM rather than from a glob, so that a draft added there
# and not here cannot go unscanned.
def fontes_do_texto() -> list[str]:
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    bloco = src.split("ORDEM: list[tuple[str, list[str]]] = [", 1)[1]
    bloco = bloco.split("\n]", 1)[0]
    nomes = re.findall(r'\("([^"]+\.md)"', bloco)
    extra = re.findall(r'^(?:LEGENDAS|ESTRUTURA) = "([^"]+)"', src, re.M)
    vistos: list[str] = []
    for n in nomes + extra:
        if n not in vistos:
            vistos.append(n)
    return vistos


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def marcadores(texto: str) -> list[int]:
    """Bracketed numerals in order of appearance, duplicates kept.

    Markdown links `[text](url)` and the drafting apparatus's own bracketed
    notes are not citations; only a bracket whose whole content is digits, or
    digits separated by commas and ranges, counts. `[1,2]` and `[3-5]` expand.
    """
    saida: list[int] = []
    for m in re.finditer(r"\[(\d[\d,\s–-]*)\]", texto):
        corpo = m.group(1)
        for parte in corpo.split(","):
            parte = parte.strip()
            if not parte:
                continue
            r = re.match(r"^(\d+)\s*[–-]\s*(\d+)$", parte)
            if r:
                a, b = int(r.group(1)), int(r.group(2))
                if a <= b:
                    saida.extend(range(a, b + 1))
                continue
            if parte.isdigit():
                saida.append(int(parte))
    return saida


def entradas(texto: str) -> list[tuple[int, str]]:
    """The reference list, as `[n] ...` lines under a '## References' heading.

    Returns (number, text). A list that does not exist yields nothing, which
    is a state and not an error: the caller decides what that means.
    """
    # The heading is matched at the START OF A LINE, and the first such
    # match wins. A plain `in`/`split` was fooled on 2026-11-09 by this very
    # file's own prose, which quotes the phrase inline while explaining that
    # no such section existed: the body then began mid-sentence and the list
    # read as empty while the markers read as pointing at nothing.
    m = re.search(r"^## References[ \t]*$", texto, re.M)
    if m is None:
        return []
    corpo = texto[m.end():]
    fim = re.search(r"^## ", corpo, re.M)
    if fim is not None:
        corpo = corpo[:fim.start()]
    saida = []
    for linha in corpo.splitlines():
        m = re.match(r"^\s*\[(\d+)\]\s+(.+)$", linha.strip())
        if m:
            saida.append((int(m.group(1)), m.group(2).strip()))
    return saida


def estado_declarado(texto: str) -> str:
    m = re.search(r"^Status:\s*\*{0,2}(\w+)", texto, re.M)
    return m.group(1).upper() if m else "NAO DECLARADO"


def main() -> int:
    ap = argparse.ArgumentParser()
    # A PROBLEM always fails; --strict additionally fails on a list that is
    # merely INCOMPLETE, which is a state and not a defect. Corrected on
    # 2026-11-02, with 18_conformidade.py, after a run there printed a defect
    # and exited 0 for want of the flag.
    ap.add_argument("--strict", action="store_true",
                    help="also fail when the reference list is incomplete, "
                         "which is a state and not a defect")
    # --dir, added 2026-11-09, for the same reason 18_conformidade.py took a
    # --src: the test that guards this script's exit code was asserting on
    # the real manuscript, so it broke the moment the real state changed --
    # it had been measuring the paper rather than the script. A test about a
    # verdict must be able to build the case it checks.
    ap.add_argument("--dir", default=str(PAPER),
                    help="the directory holding the drafts and the reference "
                         "audit (default: paper/)")
    a = ap.parse_args()
    paper = Path(a.dir)

    refs_p = paper / REFS
    if not refs_p.is_file():
        print(f"missing: {refs_p}")
        return 1
    refs_t = refs_p.read_text()
    estado = estado_declarado(refs_t)

    head("Citation state of the manuscript")
    fontes = fontes_do_texto()
    print(f"  text scanned: {len(fontes)} draft(s) named in the "
          f"consolidator's ORDEM")
    todos: list[int] = []
    por_arquivo: list[tuple[str, int]] = []
    for nome in fontes:
        p = paper / nome
        if not p.is_file():
            print(f"  MISSING SOURCE: {p}")
            return 1
        ms = marcadores(p.read_text())
        if ms:
            por_arquivo.append((nome, len(ms)))
        todos.extend(ms)
    if por_arquivo:
        for nome, n in por_arquivo:
            print(f"    {nome:<32} {n} marker(s)")
    else:
        print("    no bracketed citation marker anywhere")

    ents = entradas(refs_t)
    print(f"\n  reference list: {len(ents)} entry(ies); "
          f"declared Status: {estado}")

    # order of first appearance
    ordem: list[int] = []
    for n in todos:
        if n not in ordem:
            ordem.append(n)

    problemas: list[str] = []
    numeros = {n for n, _ in ents}
    orfaos = sorted({n for n in todos if n not in numeros})
    if orfaos:
        problemas.append(f"markers pointing at nothing: {orfaos}")
    nao_citadas = sorted(numeros - set(todos))
    if nao_citadas:
        problemas.append(f"entries never cited: {nao_citadas}")
    if ordem and ordem != sorted(ordem):
        problemas.append(
            f"numbering is not by order of appearance: first appearances are "
            f"{ordem}, and the guide requires 1, 2, 3, ...")
    faltas = [n for n, t in ents if "[FALTA:" in t]
    if faltas and estado == "COMPLETO":
        problemas.append(
            f"entries with [FALTA: in a list declared COMPLETO: {faltas}")

    head("Verdict")
    if estado != "COMPLETO":
        print(f"  The reference list declares itself {estado}.")
        print("  Nothing is approved here, and the consolidator does not emit")
        print("  a references section while that is so. The open citation")
        print(f"  points are audited in paper/{REFS}.")
    if problemas:
        for p in problemas:
            print(f"  PROBLEM: {p}")
    elif estado == "COMPLETO":
        print(f"  {len(ents)} entries, {len(ordem)} cited, numbering in order "
              f"of appearance, no missing field.")
        print("  This says the list is internally consistent. It does not say")
        print("  that any citation supports the sentence it is attached to,")
        print("  nor that the journal abbreviations follow the LTWA: both are")
        print("  reading, and neither is measured here.")

    if problemas:
        return 1
    return 1 if (a.strict and estado != "COMPLETO") else 0


if __name__ == "__main__":
    sys.exit(main())
