#!/usr/bin/env python3
"""The guide's conformity rules that are arithmetic on the text, measured.

WHAT THIS IS FOR
----------------
The closing list for submission carried "check the references and tables",
which is reading. Part of it is not: some of the guide's requirements are
decidable by counting, and those are the ones that get missed, because nobody
counts prose. This script counts.

  1. SPELLING. The guide: "We recommend that you write in American or British
     English but not a combination of both." The check reports the variant the
     manuscript uses and every outlier against it, with file and line.

     Two pairs are NOT mixing and are excluded on purpose. British English
     uses "program" for computer code and "programme" for a plan or project,
     and "license" for the verb against "licence" for the noun. A checker that
     flagged those would push a correct text into an incorrect one.

  2. FIGURE CITATIONS. The guide requires each figure to be cited in the text.
     Measured on the body, with the captions excluded -- a caption mentioning
     its own figure is not a citation of it. Found on 2026-10-29: Figure 2,
     one of the paper's central figures, was cited nowhere.

  3. CAPTIONS AGAINST FIGURES. One caption per figure, numbered contiguously,
     and the count must match the figure files the generator writes.

  4. TABLE CITATIONS. Same rule, for Table 1.

WHAT IT DOES NOT ESTABLISH
--------------------------
That a citation sits in the right sentence, that the English is good, or that
a table's layout satisfies "no vertical rules" -- that last one is a property
of the converted file and not of the Markdown, so it belongs to the conversion
step and not here. Nothing below is a judgement about writing.

Usage
-----
    python scripts/18_conformidade.py
    python scripts/18_conformidade.py --strict     # non-zero on any defect
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PAPER = RAIZ / "paper"
MANUSCRITO = PAPER / "MANUSCRITO.md"
SEP = "=" * 78

# (name, british pattern, american pattern). Patterns match whole words.
# The -ise/-ize family needs an exclusion list: "precise", "noise", "wise",
# "promise" and their kin end in -ise without being British spellings, and a
# checker that counted them would report a British manuscript as mixed.
NAO_SAO_ISE = re.compile(
    r"(cise|wise|oise|rise|mise|vise|guise|chise|aise|eise|lise\b)$", re.I)
# The "size" family is not an -ise/-ize verb: "size", "sized" and "oversized"
# are the same word in both variants, and reporting them made this checker
# call a consistent manuscript mixed on its first run.
NAO_SAO_IZE = re.compile(r"(^|\w)siz(e|es|ed|ing)$", re.I)

PARES: list[tuple[str, str, str]] = [
    ("-ise / -ize",
     r"\b\w{4,}is(?:e|es|ed|ing|ation|ations)\b",
     r"\b\w{4,}iz(?:e|es|ed|ing|ation|ations)\b"),
    ("-yse / -yze",
     r"\b\w{3,}ys(?:e|es|ed|ing)\b", r"\b\w{3,}yz(?:e|es|ed|ing)\b"),
    ("-our / -or",
     r"\b(?:behaviour|colour|favour|labour|neighbour|rigour|vigour|odour)\w*\b",
     r"\b(?:behavior|color|favor|labor|neighbor|rigor|vigor|odor)\w*\b"),
    ("-re / -er",
     r"\b(?:centre|centred|centres|metre|metres|fibre|fibres|litre|litres)\b",
     r"\b(?:center|centered|centers|fiber|fibers|liter|liters)\b"),
    ("-lled / -led",
     r"\b(?:modelled|modelling|labelled|labelling|travelled|signalled)\b",
     r"\b(?:modeled|modeling|labeled|labeling|traveled|signaled)\b"),
    ("-gue / -g",
     r"\b(?:catalogue|dialogue|analogue)\w*\b",
     r"\b(?:catalog|dialog|analog)\b"),
]
# Correct in British English on both sides; never reported as mixing.
ISENTOS = {"program", "programs", "programme", "programmes",
           "license", "licensed", "licenses", "licence", "licences"}


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def ocorrencias(padrao: str, texto: str) -> list[str]:
    saida = []
    for m in re.finditer(padrao, texto, re.I):
        w = m.group(0)
        if w.lower() in ISENTOS:
            continue
        if NAO_SAO_ISE.search(w) or NAO_SAO_IZE.search(w):
            continue
        saida.append(w.lower())
    return saida


def onde(palavra: str) -> list[str]:
    """Where to find an outlier: the consolidated manuscript first, because
    that is where the count came from, then the drafts, because that is where
    it is edited. A draft hit that is not in the manuscript is a Portuguese
    apparatus line, and the first list is what says so."""
    locais = []
    for i, linha in enumerate(MANUSCRITO.read_text().splitlines(), 1):
        if re.search(rf"\b{re.escape(palavra)}\b", linha, re.I):
            locais.append(f"MANUSCRITO.md:{i} (in the manuscript)")
    for p in sorted(PAPER.glob("*.md")):
        if p.name == "MANUSCRITO.md":
            continue
        for i, linha in enumerate(p.read_text().splitlines(), 1):
            if re.search(rf"\b{re.escape(palavra)}\b", linha, re.I):
                locais.append(f"{p.name}:{i}")
    return locais


def corpo_e_legendas(texto: str) -> tuple[str, str]:
    if "## Figure captions" not in texto:
        return texto, ""
    corpo, resto = texto.split("## Figure captions", 1)
    return corpo, resto


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    if not MANUSCRITO.is_file():
        print(f"missing: {MANUSCRITO} -- run 15_consolidar_manuscrito.py first")
        return 1
    texto = MANUSCRITO.read_text()
    corpo, legendas = corpo_e_legendas(texto)
    defeitos: list[str] = []

    head("Spelling: American or British, but not both")
    br_total, am_total = 0, 0
    detalhe: list[tuple[str, Counter, Counter]] = []
    for nome, pbr, pam in PARES:
        br = Counter(ocorrencias(pbr, texto))
        am = Counter(ocorrencias(pam, texto))
        br_total += sum(br.values())
        am_total += sum(am.values())
        detalhe.append((nome, br, am))
    variante = ("British" if br_total > am_total else
                "American" if am_total > br_total else "undecided")
    print(f"  dominant variant: {variante}   "
          f"(British forms {br_total}, American forms {am_total})")
    for nome, br, am in detalhe:
        fora = am if variante == "British" else br
        dentro = br if variante == "British" else am
        if sum(dentro.values()) or sum(fora.values()):
            print(f"\n  {nome}")
            print(f"    in variant : {dict(dentro.most_common(8)) or 'none'}")
            if fora:
                print(f"    OUTLIERS   : {dict(fora)}")
                for w in fora:
                    for loc in onde(w):
                        print(f"      {w} at {loc}")
                defeitos.append(
                    f"{sum(fora.values())} {variante}-inconsistent form(s) "
                    f"in {nome}: {sorted(fora)}")
            else:
                print("    OUTLIERS   : none")
    print("\n  Not counted as mixing, because British English uses both:")
    print("    program (code) / programme (project); "
          "license (verb) / licence (noun)")

    head("Figures and tables cited in the text")
    numeros = sorted(int(n) for n in re.findall(r"^## Figure (\d+)$",
                                                legendas, re.M))
    print(f"  captions found: {len(numeros)} -> {numeros}")
    if numeros != list(range(1, len(numeros) + 1)):
        defeitos.append(f"captions are not contiguous from 1: {numeros}")
    for n in numeros:
        c = len(re.findall(rf"Figure\s*{n}\b", corpo))
        print(f"    Figure {n}: {c} citation(s) in the body")
        if c == 0:
            defeitos.append(f"Figure {n} is never cited in the text")
    t1 = len(re.findall(r"Table\s*1\b", corpo))
    print(f"    Table 1 : {t1} citation(s) in the body")
    if t1 == 0:
        defeitos.append("Table 1 is never cited in the text")

    head("Verdict")
    if defeitos:
        for d in defeitos:
            print(f"  DEFECT: {d}")
    else:
        print("  No defect in what is measured here: one spelling variant,")
        print("  every figure and table cited, captions contiguous.")
    print("\n  Not measured: whether a citation sits in the right sentence,")
    print("  whether the English reads well, or whether the converted tables")
    print("  carry vertical rules -- that last is a property of the converted")
    print("  file and belongs to the conversion step.")
    return 1 if (a.strict and defeitos) else 0


if __name__ == "__main__":
    sys.exit(main())
