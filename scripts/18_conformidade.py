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

     AUTHORIAL PROSE AND VERBATIM QUOTATION ARE COUNTED APART, by the author's
     decision of 2026-10-29: a quotation is reproduced as it was written, so
     an outlier inside one is not a defect, and British spelling is required
     of authorial prose only. The manuscript's quotations are blockquotes,
     lines beginning "> ", which is what the split is measured on. A checker
     that demanded one variant everywhere would be asking for a quotation to
     be altered.

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

  5. LANGUAGE OF THE ARTEFACT. The manuscript is English, and anything in the
     drafting language that reaches it is a defect of the submitted file, not
     a matter of style. Measured by unambiguous Portuguese markers -- accented
     forms and function words with no English homograph -- reported BY SECTION,
     because where it is decides what it is. Found on 2026-10-29: Table 1, the
     paper's only table and the record of all twenty pre-registered
     hypotheses, entirely in Portuguese; and a drafting pendency note inside
     Section 9.3. The note was moved to paper/correcao-em-provas.md verbatim
     the same day; the table is proposed for translation in 13-tabela1.md and
     awaits the author.

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

# Unambiguous Portuguese: accented forms, and function words that are not
# English words. "a", "e", "no", "da" are excluded on purpose -- they occur in
# English text and in identifiers, and a marker list that fires on them would
# report every page as mixed.
MARCADORES_PT = (
    r"\b(não|também|são|está|já|até|após|pelo|pela|uma|dos|das|pré|"
    r"veredito|critério|suportada|enunciado|platô|empate|decil|piso|faixa|"
    r"contagem|leitura|redação|parcial|achado|reversão|idem|"
    r"construção|partição|partições|cláusula|vizinhança|teto)\b"
)

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


# Sections that are reproduced records and not authorial prose: their
# spelling and their language belong to whoever wrote the names in them.
# The CRediT statement joined them on 2026-11-11: "Conceptualization" and
# "Visualization" are the fixed names of roles in the CRediT taxonomy, not
# this manuscript's spelling choices, and respelling them -isation would
# corrupt the taxonomy to satisfy a rule about authorial prose.
SECOES_REPRODUZIDAS = frozenset({"References", "Authors",
                                 "CRediT authorship contribution statement",
                                 "Declaration of Generative AI and AI-assisted technologies in the writing process"})


def sem_identificadores(texto: str) -> str:
    """Removes URLs, DOIs and inline code spans before any spelling count.

    They are NAMES, not spelling choices, wherever they sit. The repository
    this manuscript cites is called `pgsg3-gate-regularization-path`, with a
    -z that belongs to the repository and not to the prose; counting it made
    the Data availability section fail the British-English rule on
    2026-11-16.

    Exempting that whole section would have been the blunt instrument: the
    section IS authorial prose, and a real misspelling in it must still be
    caught -- verified, by planting one and watching the check fail. Removing
    the identifiers instead leaves the prose around them scanned as prose.

    Applied to the counting text AND to the authorial/quoted split, so the
    report adds up. Applied to only one of them, an outlier appeared in the
    OUTLIERS line and in neither of the two lines that account for it.
    """
    texto = re.sub(r"`[^`\n]*`", " ", texto)
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"\bdoi:\S+", " ", texto)
    return texto


def separa_citacoes(texto: str) -> tuple[str, str]:
    """(authorial prose, verbatim quotation), split on blockquote markers.

    A quotation in this manuscript is a blockquote. The caption block is one
    too, and captions ARE authorial, so the split is applied to the body only
    -- the caller passes the body, and the captions come back through the
    authorial side.

    THE REFERENCE LIST goes to the quoted side as well, from 2026-11-09. A
    reference is reproduced, not written: the author names, the article
    titles and the journal names are other people's strings and correcting
    their spelling would corrupt the record. The first run with a list
    proved the point twice over -- it reported `laboratory` as an American
    -our/-or form, from the journal name *Chemometrics and Intelligent
    Laboratory Systems*, and a Portuguese marker from the author name *de
    Lima das Chagas*. Both are correct as they stand and neither is this
    manuscript's prose.
    """
    texto = sem_identificadores(texto)
    autoral, citado = [], []
    em_referencias = False
    for linha in texto.splitlines():
        if re.match(r"^## ", linha):
            em_referencias = linha.strip().removeprefix("## ") in SECOES_REPRODUZIDAS
        if em_referencias or linha.lstrip().startswith(">"):
            citado.append(linha)
        else:
            autoral.append(linha)
    return "\n".join(autoral), "\n".join(citado)


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


def onde(palavra: str, fonte: Path = MANUSCRITO) -> list[str]:
    """Where to find an outlier: the consolidated manuscript first, because
    that is where the count came from, then the drafts, because that is where
    it is edited. A draft hit that is not in the manuscript is a Portuguese
    apparatus line, and the first list is what says so.

    The scanned file is passed in rather than read from the module, so that
    --src reports the lines of the file it actually scanned."""
    locais = []
    for i, linha in enumerate(fonte.read_text().splitlines(), 1):
        if re.search(rf"\b{re.escape(palavra)}\b", linha, re.I):
            locais.append(f"{fonte.name}:{i} (in the manuscript)")
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
    # A DEFECT ALWAYS FAILS, with or without the flag. On 2026-11-02 the
    # author ran this script without --strict: it printed
    # "DEFECT: 74 Portuguese marker(s)" and exited 0, so `echo $?` reported
    # "conformidade: 0" directly under its own verdict. An exit code that
    # contradicts the report is the same class of defect as the standard
    # deviation this programme once printed as 0.0000 while computing a z from
    # it: a display hiding the quantity it reports on. --strict now adds only
    # the stricter condition -- failing when a check could not be MADE -- and
    # takes nothing away from the defect verdict.
    ap.add_argument("--strict", action="store_true",
                    help="also fail when a check could not be made at all, "
                         "not only when it found a defect")
    # --src, added 2026-11-09. Until then the only way to exercise this
    # script's verdict was to run it on the real manuscript, and the test
    # that guards the exit code did exactly that -- it asserted that a DEFECT
    # was printed, using the Portuguese Table 1 as its fixture. When the
    # table was translated the defect went away and the test failed, having
    # been measuring the manuscript rather than the script. A test about a
    # verdict has to be able to construct the case it checks.
    ap.add_argument("--src", default=str(MANUSCRITO),
                    help="the consolidated manuscript to scan "
                         "(default: paper/MANUSCRITO.md)")
    a = ap.parse_args()
    fonte = Path(a.src)
    if not fonte.is_file():
        print(f"missing: {fonte} -- run 15_consolidar_manuscrito.py first")
        return 1
    texto = fonte.read_text()
    corpo, legendas = corpo_e_legendas(texto)
    defeitos: list[str] = []

    head("Spelling: American or British, but not both")
    # Captions are blockquotes and are authorial, so they are moved to the
    # authorial side before the split is read.
    autoral_corpo, citado = separa_citacoes(corpo)
    autoral = autoral_corpo + "\n" + sem_identificadores(legendas)
    corpo = sem_identificadores(corpo)
    br_total, am_total = 0, 0
    detalhe: list[tuple[str, Counter, Counter]] = []
    for nome, pbr, pam in PARES:
        br = Counter(ocorrencias(pbr, corpo))
        am = Counter(ocorrencias(pam, corpo))
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
            if not fora:
                print("    OUTLIERS   : none")
                continue
            pbr = next(p for n, p, _ in PARES if n == nome)
            pam = next(p for n, _, p in PARES if n == nome)
            padrao_fora = pam if variante == "British" else pbr
            em_autoral = Counter(ocorrencias(padrao_fora, autoral))
            em_citado = Counter(ocorrencias(padrao_fora, citado))
            print(f"    OUTLIERS   : {dict(fora)}")
            print(f"      in authorial prose : "
                  f"{dict(em_autoral) or 'none'}")
            print(f"      in verbatim quotes : "
                  f"{dict(em_citado) or 'none'}   (exempt: a quotation is "
                  f"reproduced, not spelled)")
            for w in fora:
                for loc in onde(w, fonte):
                    print(f"      {w} at {loc}")
            if em_autoral:
                defeitos.append(
                    f"{sum(em_autoral.values())} {variante}-inconsistent "
                    f"form(s) in AUTHORIAL prose, {nome}: "
                    f"{sorted(em_autoral)}")
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

    head("Language of the artefact: the manuscript is English")
    por_secao: Counter = Counter()
    atual = "(header)"
    for linha in texto.splitlines():
        if linha.startswith("## "):
            atual = linha[3:].strip()
        # Two sections are exempt here, for the same reason they are exempt
        # from the spelling check: they are RECORDS, reproduced rather than
        # written, and the Portuguese in them belongs to names.
        #
        #   References -- "de Lima das Chagas" is a person's name.
        #   Authors    -- "Pontifícia Universidade Católica de Goiás" is an
        #                 institution's legal name and "Setor Leste
        #                 Universitário" is a street address. Translating
        #                 either would make the affiliation wrong, and the
        #                 guide asks for the affiliation, not a rendering of
        #                 it. Added 2026-11-10 with the title page.
        if atual in SECOES_REPRODUZIDAS:
            continue
        achados = re.findall(MARCADORES_PT, linha, re.I)
        if achados:
            por_secao[atual] += len(achados)
    if not por_secao:
        print("  no Portuguese marker anywhere in the manuscript")
    else:
        print("  Portuguese markers, by section of the manuscript:")
        for sec, n in por_secao.most_common():
            print(f"    {n:4d}  {sec}")
        total = sum(por_secao.values())
        defeitos.append(
            f"{total} Portuguese marker(s) in the English manuscript, in "
            f"{len(por_secao)} section(s): {sorted(por_secao)}")
        print("\n  A section of the submitted file in the drafting language is")
        print("  a defect of the file, not a matter of style. Table 1, if it")
        print("  is listed above, has a translation proposed in")
        print("  paper/13-tabela1.md, not yet approved by the author.")

    head("Verdict")
    if defeitos:
        for d in defeitos:
            print(f"  DEFECT: {d}")
    else:
        print("  No defect in what is measured here: one spelling variant in")
        print("  authorial prose, every figure and table cited, captions")
        print("  contiguous. An outlier inside a verbatim quotation, if any is")
        print("  listed above, is exempt by the author's decision of")
        print("  2026-10-29 and is not counted as a defect.")
    print("\n  Not measured: whether a citation sits in the right sentence,")
    print("  whether the English reads well, or whether the converted tables")
    print("  carry vertical rules -- that last is a property of the converted")
    print("  file and belongs to the conversion step.")
    if defeitos:
        return 1
    if a.strict and not numeros:
        print("\n  --strict: no caption was found, so the figure checks were "
              "not made. Reporting that as a failure rather than as a pass.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
