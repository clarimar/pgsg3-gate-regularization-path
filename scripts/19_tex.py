#!/usr/bin/env python3
"""Build a LaTeX reading copy of the manuscript from paper/MANUSCRITO.md.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
It is a READING COPY: a .tex that compiles, so the manuscript can be read as a
document instead of as Markdown. It is not the submission file.

Three things are missing from the submission file and no converter can supply
them, so they are declared in the output rather than papered over:

  - THE TITLE PAGE. The guide requires given and family names, affiliations
    with full postal address and country, and the corresponding author's email.
    Those are the authors' facts. The output carries the title, which is
    settled, and a visible placeholder where the author block belongs.
  - THE REFERENCES. The manuscript has none; the audit of what requires a
    citation is in paper/12-referencias.md. The output says so in the place
    where the reference list goes, rather than leaving a silence a reader would
    take for an omission in the conversion.
  - THE CLASS. Elsevier's elsarticle.cls is not installed here, so a file
    built against it could not be compiled before delivery, and this programme
    does not deliver what it has not run. The reading copy uses `article`. The
    submission file will use elsarticle, whose front matter is different, and
    is worth generating when the title-page facts exist.

Table 1 is emitted as it stands. Since 2026-11-09 it comes from
paper/13-tabela1.md, in English and reconciled row by row against the
Portuguese original in 00-estrutura.md by the consolidator; the conversion is
not the place to decide either.

WHAT IT REFUSES TO DO
---------------------
Silently mangle. Every Markdown construct found in the source is handled
explicitly, every non-ASCII character is mapped explicitly, and anything
unrecognised stops the build with the line that caused it. A converter that
guesses produces a document that looks right and says something else.

Usage
-----
    python scripts/19_tex.py                 # writes paper/MANUSCRITO.tex
    python scripts/19_tex.py --out other.tex
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "paper" / "MANUSCRITO.md"
FIGURAS = {
    1: "figuras/fig1_prior_degrau.pdf",
    2: "figuras/fig2_colapso_por_desempate.pdf",
    3: "figuras/fig3_resposta_ao_tamanho.pdf",
    4: "figuras/fig4_controle_raman.pdf",
    5: "figuras/fig5_alinhamento_intra_nivel.pdf",
}

# Non-ASCII mapped explicitly. pdfLaTeX with inputenc handles the accented
# Latin letters of the Portuguese table; everything else needs a macro, and a
# character absent from this table stops the build rather than reaching the
# output as a byte pdfLaTeX will reject.
# ö and ß joined the set on 2026-11-09, with the reference list: German
# and Swedish author names (Kögler, Bießmann, Sjöström) reach the
# converter for the first time, and inputenc handles both.
ACENTOS = "áâãàçéêíóôõúüÁÂÃÀÇÉÊÍÓÔÕÚÜñÑöÖäÄåÅøØßæÆ"
SIMBOLOS = {
    "—": "---", "–": "--", "−": "$-$", "…": "\\ldots{}",
    "±": "$\\pm$", "×": "$\\times$", "·": "$\\cdot$",
    "≥": "$\\geq$", "≤": "$\\leq$", "≈": "$\\approx$",
    "∩": "$\\cap$", "∪": "$\\cup$", "∞": "$\\infty$", "¬": "$\\neg$",
    "→": "$\\rightarrow$", "‖": "$\\|$", "′": "$'$", "″": "$''$",
    "§": "\\S{}", "°": "$^{\\circ}$", "≠": "$\\neq$", "⇒": "$\\Rightarrow$",
    "θ": "$\\theta$", "λ": "$\\lambda$", "ρ": "$\\rho$", "σ": "$\\sigma$",
    "Σ": "$\\Sigma$", "μ": "$\\mu$", "α": "$\\alpha$", "β": "$\\beta$",
    "δ": "$\\delta$", "Δ": "$\\Delta$", "ε": "$\\varepsilon$",
    "π": "$\\pi$", "τ": "$\\tau$", "φ": "$\\varphi$", "χ": "$\\chi$",
    "ω": "$\\omega$", "Θ": "$\\Theta$",
    # U+2217, the asterisk operator, arrived on 2026-11-10 with the title
    # page: it is the corresponding-author marker, which the author wrote as
    # that glyph and not as a plain asterisk. Mapped and not normalised to
    # "*", because the two are different characters and the author chose one.
    "∗": "$\\ast$",
}
SUPER = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
         "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-", "⁺": "+",
         "⁽": "(", "⁾": ")", "ᵃ": "a", "ᵇ": "b", "ⁿ": "n", "ⁱ": "i"}
SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
       "₆": "6", "₇": "7", "₈": "8", "₉": "9", "ₖ": "k", "ₙ": "n",
       "ᵢ": "i", "ⱼ": "j", "₋": "-", "ₚ": "p"}

ESPECIAIS = {"\\": "\\textbackslash{}", "&": "\\&", "%": "\\%", "$": "\\$",
             "#": "\\#", "_": "\\_", "{": "\\{", "}": "\\}",
             "~": "\\textasciitilde{}", "^": "\\textasciicircum{}"}


def inline(s: str, *, onde: str = "") -> str:
    """One line of Markdown prose to LaTeX, in an order that cannot collide.

    Code spans are lifted out first, so that the escaping below cannot eat
    their backticks and so that their contents are escaped once; then the
    LaTeX specials are escaped; then the non-ASCII characters are mapped,
    which is the only step that INSERTS backslashes and dollars; then the
    emphasis markers, which are plain ASCII and survive the earlier steps.
    """
    guardados: list[str] = []

    def guarda(m: re.Match) -> str:
        guardados.append(m.group(1))
        return f"\x00{len(guardados) - 1}\x00"

    s = re.sub(r"`([^`]+)`", guarda, s)
    # The source uses &nbsp; to indent a displayed formula. Escaped as text it
    # printed "&nbsp;" in the PDF; it is a tie.
    s = s.replace("&nbsp;", "\x01")

    s = "".join(ESPECIAIS.get(ch, ch) for ch in s)

    # runs of super/subscript characters become one script group
    def grupo(tab: dict[str, str], marca: str) -> None:
        nonlocal s
        classe = "".join(re.escape(c) for c in tab)
        s = re.sub(f"([{classe}]+)",
                   lambda m: "$" + marca + "{"
                             + "".join(tab[c] for c in m.group(1)) + "}$",
                   s)

    grupo(SUPER, "^")
    grupo(SUB, "_")

    fora = []
    for ch in s:
        if ord(ch) < 128 or ch in ACENTOS:
            fora.append(ch)
        elif ch in SIMBOLOS:
            fora.append(SIMBOLOS[ch])
        else:
            raise SystemExit(
                f"19_tex: unmapped character {ch!r} (U+{ord(ch):04X})"
                f"{' in ' + onde if onde else ''}. Add it to SIMBOLOS, SUPER "
                f"or SUB -- the build stops rather than emitting a byte "
                f"pdfLaTeX will reject.")
    s = "".join(fora).replace("\x01", "~")

    # Adjacent math groups come out of the character mapping as "$\\Sigma$$_{k}$";
    # closing and reopening between them is harmless but ugly, and merging is
    # safe here because a literal dollar was escaped to "\\$" long before.
    s = s.replace("$$", "")

    # Markdown's backslash escape: "\*" means a literal asterisk, and Table 1
    # writes the optimal lambda as "lambda\*". Escaped as a LaTeX special it
    # printed "\textbackslash{}*" in the PDF, which the referee of
    # 2026-11-10 read as a surviving edit mark. Lifted out BEFORE the
    # emphasis markers run, so that it cannot open one, and restored after.
    s = s.replace("\\textbackslash{}*", "\x02")

    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"\\emph{\1}", s)
    s = s.replace("\x02", "$^{*}$")

    for i, codigo in enumerate(guardados):
        # Inside \texttt a script cannot be set with math without looking
        # wrong, so the text-mode commands are used. The first build left a
        # subscript zero unmapped here, because this path handled SIMBOLOS
        # only: a code span is text too, and the same table has to cover it.
        partes = []
        for ch in codigo:
            if ch in ESPECIAIS:
                partes.append(ESPECIAIS[ch])
            elif ord(ch) < 128 or ch in ACENTOS:
                partes.append(ch)
            elif ch in SUB:
                partes.append("\\textsubscript{" + SUB[ch] + "}")
            elif ch in SUPER:
                partes.append("\\textsuperscript{" + SUPER[ch] + "}")
            elif ch in SIMBOLOS:
                partes.append(SIMBOLOS[ch])
            else:
                raise SystemExit(
                    f"19_tex: unmapped character {ch!r} (U+{ord(ch):04X}) "
                    f"inside a code span{' in ' + onde if onde else ''}.")
        # A typewriter run does not hyphenate, so a long path is one
        # unbreakable box: scripts/14_etapa_b_por_procedimento.py ran 60.9pt
        # past the margin in the build of 2026-11-10. Break points are offered
        # after each separator -- \allowbreak only permits a break, it never
        # forces one, so a path that fits is still set on one line.
        corpo = "".join(partes)
        for sep in ("\\_", "/", "."):
            corpo = corpo.replace(sep, sep + "\\allowbreak{}")
        s = s.replace(f"\x00{i}\x00", "\\texttt{" + corpo + "}")
    return s


def blocos(texto: str) -> list[tuple[str, list[str]]]:
    saida: list[tuple[str, list[str]]] = []
    titulo, corpo = "__CABECA__", []
    for linha in texto.splitlines():
        if linha.startswith("## "):
            saida.append((titulo, corpo))
            titulo, corpo = linha[3:].strip(), []
        else:
            corpo.append(linha)
    saida.append((titulo, corpo))
    return saida


def tabela(linhas: list[str], *, longa: bool) -> list[str]:
    """A Markdown pipe table as booktabs: no vertical rules, which the guide
    requires, and no shading. Long cells get a p{} column so the row wraps
    instead of running off the page."""
    celulas = [[c.strip() for c in l.strip().strip("|").split("|")]
               for l in linhas if not re.match(r"^\|[\s:|-]+\|?$", l.strip())]
    n = max(len(r) for r in celulas)
    celulas = [r + [""] * (n - len(r)) for r in celulas]
    # Column weights. Proportional to the LONGEST cell is the obvious rule and
    # it is wrong: Table 1 has one cell of ~400 characters, which took 83% of
    # the width and squeezed the hypothesis labels into a column one character
    # wide, breaking "H7-shuffled" down the page. A column needs at least the
    # width of its longest unbreakable word, and beyond that the MEAN cell is
    # the honest measure of how much text it carries.
    def medidas(i: int) -> tuple[float, float]:
        textos = [r[i] for r in celulas]
        palavra = max((len(w) for t in textos for w in t.split()), default=1)
        media = sum(len(t) for t in textos) / max(1, len(textos))
        return float(palavra), float(media)

    pares = [medidas(i) for i in range(n)]
    larg = [max(p_, m_) for p_, m_ in pares]
    total = sum(larg) or 1
    if max(len(r[i]) for r in celulas for i in range(n)) > 40:
        # Each column pair carries 2*\tabcolsep of its own, so a spec that
        # shares out the full \linewidth overflows by that much: the first
        # build produced some forty overfull boxes in Table 1 alone. The
        # fraction left for the text is reduced by the separation the columns
        # will add back.
        util = max(0.5, 0.98 - 0.035 * n)
        # The longest word is a MINIMUM, not a weight. Expressed as a weight it
        # still loses to a cell of four hundred characters, which is the case
        # Table 1 actually contains: the label column came out at 2% of the
        # line, ten points, and "H7-shuffled" broke down the page. So the
        # minimums are assigned first -- about 85 characters fit on a line at
        # this size -- and only what is left over is shared out by mean length.
        minimos = [min(0.30, p_ / 85.0) for p_, _ in pares]
        folga = util - sum(minimos)
        if folga <= 0:
            escala = util / sum(minimos)
            fracoes = [x * escala for x in minimos]
        else:
            soma_media = sum(m_ for _, m_ in pares) or 1.0
            fracoes = [mi + folga * m_ / soma_media
                       for mi, (_, m_) in zip(minimos, pares)]
        spec = "".join("P{%.3f\\linewidth}" % f for f in fracoes)
    else:
        spec = "l" * n
    env = "longtable" if longa else "tabular"
    fora = [f"\\begin{{{env}}}{{{spec}}}", "\\toprule"]
    for i, r in enumerate(celulas):
        fora.append(" & ".join(inline(c, onde="table") for c in r) + " \\\\")
        if i == 0:
            fora.append("\\midrule")
            if longa:
                fora.append("\\endhead")
    fora += ["\\bottomrule", f"\\end{{{env}}}"]
    if not longa:
        fora = ["\\begin{center}\\small"] + fora + ["\\end{center}"]
    else:
        fora = ["{\\small"] + fora + ["}"]
    return fora


def corpo_para_tex(linhas: list[str], *, onde: str) -> list[str]:
    """Prose, quotations, tables, lists and the one indented display line.
    Anything else stops the build."""
    fora: list[str] = []
    i, n = 0, len(linhas)
    while i < n:
        l = linhas[i]
        s = l.strip()
        if not s or s == "---":
            fora.append("")
            i += 1
        elif s.startswith("### ") or s.startswith("#### "):
            # The LEVEL comes from the depth of the heading's own number, not
            # from the number of hashes. The manuscript writes 4.2 and 4.2.1
            # both as "###", and mapping by hashes made 4.2.1 a subsection:
            # LaTeX then renumbered it 4.3 and shifted every number after it,
            # so "Section 4.3" in the text pointed at what the page printed as
            # 4.4. The referee of 2026-11-02 found it as a missing 4.2.1; it
            # was worse than that, and silent.
            m = re.match(r"^#+\s*((?:\d+\.)+\d*)\s*(.*)$", s)
            if m:
                profundidade = len([x for x in m.group(1).split(".") if x])
                titulo_h = m.group(2)
            else:
                profundidade = 3 if s.startswith("#### ") else 2
                titulo_h = re.sub(r"^#+\s*", "", s)
            comando = {2: "subsection", 3: "subsubsection"}.get(
                profundidade, "paragraph")
            fora.append("\\" + comando + "{"
                        + inline(titulo_h, onde=onde) + "}")
            i += 1
        elif s.startswith("|"):
            j = i
            while j < n and linhas[j].strip().startswith("|"):
                j += 1
            fora += tabela(linhas[i:j], longa=(j - i) > 12)
            i = j
        elif s.startswith(">"):
            j = i
            dentro = []
            while j < n and linhas[j].strip().startswith(">"):
                dentro.append(re.sub(r"^\s*>\s?", "", linhas[j]))
                j += 1
            fora.append("\\begin{quote}")
            fora += [inline(x, onde=onde) if x.strip() else ""
                     for x in dentro]
            fora.append("\\end{quote}")
            i = j
        elif re.match(r"^[-*] ", s) or re.match(r"^\d+\. ", s):
            # A list item CONTINUES over the draft's line wrap. Until
            # 2026-11-10 each source line was its own item, so an item that
            # wrapped closed the environment, the continuation printed as a
            # loose paragraph, and the next item opened a NEW enumerate --
            # which is why the PDF showed several lists all numbered "1.".
            # A continuation is a non-empty line that starts no marker.
            numerada = bool(re.match(r"^\d+\. ", s))
            marcador = r"^\d+\. " if numerada else r"^[-*] "
            j, itens = i, []
            while j < n and re.match(marcador, linhas[j].strip()):
                item = [re.sub(marcador, "", linhas[j].strip())]
                j += 1
                while (j < n and linhas[j].strip()
                       and not re.match(r"^[-*] |^\d+\. |^#{1,6} |^>|^\|",
                                        linhas[j].strip())
                       and not linhas[j].startswith(("    ", "\t"))):
                    item.append(linhas[j].strip())
                    j += 1
                itens.append(" ".join(item))
            amb = "enumerate" if numerada else "itemize"
            fora.append("\\begin{" + amb + "}")
            fora += ["\\item " + inline(x, onde=onde) for x in itens]
            fora.append("\\end{" + amb + "}")
            i = j
        elif l.startswith("    ") or l.startswith("\t"):
            fora.append("\\begin{quote}\\ttfamily\\small")
            while i < n and (linhas[i].startswith("    ")
                             or linhas[i].startswith("\t")):
                fora.append(inline(linhas[i].strip(), onde=onde) + "\\\\")
                i += 1
            fora.append("\\end{quote}")
        else:
            # PROSE BY PARAGRAPH, not by line. Emphasis is written across the
            # draft's 79-column wrap -- "**That overlap has to be read\n
            # against chance...**" -- and a line-wise conversion never
            # matched it, so fifty "**" and eight "*" reached the PDF as
            # literal asterisks. The referee of 2026-11-10 saw them as
            # surviving edit marks, which is exactly what they were.
            j, par = i, []
            while (j < n and linhas[j].strip()
                   and linhas[j].strip() != "---"
                   and not re.match(r"^#{1,6} |^[-*] |^\d+\. |^>|^\|",
                                    linhas[j].strip())
                   and not linhas[j].startswith(("    ", "\t"))):
                par.append(linhas[j].strip())
                j += 1
            fora.append(inline(" ".join(par), onde=onde))
            i = j if j > i else i + 1
    return fora


def confere_numeracao(secoes: list[tuple[str, list[str]]]) -> list[str]:
    """The numbers LaTeX will print must be the numbers the manuscript wrote.

    LaTeX numbers sections from its own counters, and the manuscript carries
    its numbers in the text -- "Section 4.2.1", "Section 9.3.2" -- as words,
    not as references. If the two disagree, every cross-reference in the paper
    points at the wrong place and nothing says so: the document compiles, the
    numbers look plausible, and only a reader following a reference finds out.
    That is what happened when 4.2.1 was emitted as a subsection.

    So the counters are simulated here and compared with what is written. A
    mismatch stops the build.
    """
    problemas: list[str] = []
    sec = sub = subsub = 0
    for titulo, corpo in secoes:
        m = re.match(r"^(\d+)\.\s", titulo)
        if m:
            sec, sub, subsub = int(m.group(1)), 0, 0
            if sec != int(m.group(1)):
                problemas.append(titulo)
        for linha in corpo:
            h = re.match(r"^(#{3,4})\s*((?:\d+\.)+\d*)\s", linha.strip())
            if not h:
                continue
            partes = [int(x) for x in h.group(2).split(".") if x]
            if len(partes) == 2:
                sub += 1
                subsub = 0
                esperado = [sec, sub]
            elif len(partes) == 3:
                subsub += 1
                esperado = [sec, sub, subsub]
            else:
                problemas.append(f"{h.group(2)}: unexpected depth")
                continue
            if partes != esperado:
                problemas.append(
                    f"the manuscript writes {h.group(2)} where LaTeX will "
                    f"print {'.'.join(str(x) for x in esperado)}")
    return problemas


PREAMBULO = r"""% Reading copy, generated by scripts/19_tex.py -- do not edit by hand.
% Compiles with pdfLaTeX. For the figures to appear, put the five PDFs of
% paper/figuras/ in a figuras/ folder beside this file; without them the
% build still succeeds and each figure shows a framed placeholder.
%
% NOT THE SUBMISSION FILE. The journal takes elsarticle.cls, whose front
% matter differs: the authors, affiliations and corresponding author are set
% here in a plain \author block, from paper/16-pagina-de-titulo.md, and will
% have to be re-expressed in that class's own commands. The reference list is
% reproduced from paper/12-referencias.md as a typed enumerate, not from
% BibTeX; paper/referencias.bib is the record to submit.
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
% Latin Modern is not installed in the environment this file is built and
% compiled in, and it is on Overleaf. Guarding it keeps one file that compiles
% in both places: the font is used where it exists, and the build does not
% stop where it does not. A file delivered without being compiled is not
% delivered in this programme.
\IfFileExists{lmodern.sty}{\usepackage{lmodern}}{}
\IfFileExists{babel.sty}{\usepackage[english]{babel}}{}
\usepackage{amsmath,amssymb,textcomp}
\usepackage{array,booktabs,longtable}
% Paragraph columns are set ragged right. Justified in a column a few words
% wide, Table 1 hyphenated "maxi-mum", "con-tent", "distin-guishes" and
% "Ra-man" and stretched the interword space to match, which the referee of
% 2026-11-10 read as fragmented sentences. Ragged right removes the stretch
% and with it most of the breaks; nothing about the content changes.
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}
\usepackage{graphicx}
\usepackage[margin=2.5cm]{geometry}
\usepackage{parskip}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\setcounter{secnumdepth}{3}
\setlength{\emergencystretch}{3em}
% The placeholder takes an ALREADY ESCAPED file name: the real names carry
% underscores, and passing them raw put LaTeX into math mode and filled the
% log with "Missing $ inserted" for anyone compiling the .tex on its own.
\providecommand{\semfigura}[1]{%
  \fbox{\parbox[c][0.28\textheight][c]{0.88\linewidth}{\centering\small
  Figure file not found: \texttt{#1}\par\medskip
  Put the five PDFs of \texttt{paper/figuras/} in a \texttt{figuras/} folder
  beside this \texttt{.tex}.}}}
% Figures are included at the size they were DRAWN, and scaled down only if
% they would overflow the text block. Forcing width=\linewidth on all five
% magnified the three narrow ones by 1.43x to 1.93x, so the same 7pt tick
% label printed at 7pt in one figure and at 13pt in another; the referee of
% 2026-11-10 read the smallest of them as hard to read. Scale 1 everywhere is
% what makes the font sizes declared in scripts/10_figuras.py the font sizes
% on the page.
\newsavebox{\caixafigura}
\providecommand{\figuranatural}[1]{%
  \sbox{\caixafigura}{\includegraphics{#1}}%
  \ifdim\wd\caixafigura>\linewidth
    \includegraphics[width=\linewidth]{#1}%
  \else
    \usebox{\caixafigura}%
  \fi}
"""


def bib_para_submissao(origem: Path, destino: Path) -> int:
    """Writes a submission copy of the .bib with the `note` fields removed.

    paper/referencias.bib is the RECORD: each entry's note says where every
    field was read, what came from a reference list rather than the article,
    and what is still outstanding. That is the audit, and it belongs in the
    repository.

    It does not belong in the manuscript. `unsrt` prints `note`, so citing
    against the record directly puts "Read the PDF on the author's own site,
    including Definition 1 and the hypergeometric expectation E[r] = k^2/n"
    inside the paper's reference list -- which is both wrong and, because the
    notes hold raw mathematics, a LaTeX error. Measured on the first attempt:
    240 lines of .bbl for 21 references, and four errors.

    Nothing else is touched: same keys, same fields, same values.
    """
    texto = origem.read_text()
    saida, i = [], 0
    while True:
        m = re.search(r"\n\s*note\s*=\s*\{", texto[i:])
        if not m:
            saida.append(texto[i:])
            break
        saida.append(texto[i:i + m.start()])
        j = i + m.end()          # primeiro caractere dentro da chave
        nivel = 1
        while j < len(texto) and nivel:
            nivel += (texto[j] == "{") - (texto[j] == "}")
            j += 1
        # engole a virgula que separava o campo, se houver
        while j < len(texto) and texto[j] in " \t":
            j += 1
        if j < len(texto) and texto[j] == ",":
            j += 1
        i = j
    limpo = "".join(saida)
    # a virgula do campo anterior pode ter ficado pendurada antes do fecho
    limpo = re.sub(r",(\s*)\n\}", r"\1\n}", limpo)
    chaves = lambda s: re.findall(r"^@\w+\{([^,]+),", s, re.M)
    if chaves(limpo) != chaves(texto):
        print("19_tex --bib: stripping the notes changed the key list. "
              "Refusing to write a bibliography that cites other works.")
        return 0
    # Comments are stripped BEFORE looking, and the search runs on the
    # stripped text. Written the other way round, the check searched the raw
    # text inside a guard computed on the stripped one, so a surviving field
    # would have been reported only when another one existed outside a
    # comment. The commented stub for the submitted work must not trip this:
    # it carries no at-sign precisely so that bibtex cannot see it.
    sem_comentario = re.sub(r"(?m)^\s*%.*$", "", limpo)
    sobrando = re.findall(r"note\s*=", sem_comentario)
    if sobrando:
        print(f"19_tex --bib: {len(sobrando)} note fields survived the "
              "strip. Refusing to print the audit trail in the paper.")
        return 0
    destino.write_text(limpo)
    return len(chaves(limpo))


def mapa_citacoes() -> dict[str, str]:
    """Reads the number-to-key table from paper/12-referencias.md.

    The table is written once, by title matching with a bijection required,
    and recorded there (see "Mapa de numeros para chaves BibTeX"). It is READ
    here rather than recomputed: the file holds two Anderson entries, two
    Lange and two Coelho, and a build-time heuristic would be deciding
    silently which work each marker cites.
    """
    fonte = RAIZ / "paper" / "12-referencias.md"
    texto = fonte.read_text()
    m = re.search(r"^## Mapa de n.meros para chaves BibTeX[ \t]*$", texto, re.M)
    if not m:
        return {}
    corpo = texto[m.end():]
    f = re.search(r"^## ", corpo, re.M)
    pares = re.findall(r"^\|\s*\[(\d+)\]\s*\|\s*`([^`]+)`\s*\|",
                       corpo[:f.start() if f else None], re.M)
    return {n_: k for n_, k in pares}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(RAIZ / "paper" / "MANUSCRITO.tex"))
    # The source is an argument so that a test can build from a manuscript it
    # generated itself, into a directory of its own. Pinning both to the
    # repository made two tests depend on a GENERATED file being up to date:
    # they passed here and failed in the clean clone, where the committed
    # manuscript predates the title this build added.
    ap.add_argument("--src", default=str(FONTE))
    # --bib emits \cite{} against paper/referencias.bib instead of literal
    # [n] markers and a typed list. The journal's production chain expects
    # that form, and it is what lets a reference be added or reordered
    # without renumbering every marker by hand. The default stays as it was,
    # so nothing that depends on the typed list changes.
    ap.add_argument("--bib", action="store_true",
                    help="emit \\cite{} and a BibTeX bibliography")
    a = ap.parse_args()
    fonte = Path(a.src).expanduser()
    if not fonte.is_file():
        print(f"missing: {fonte} -- run 15_consolidar_manuscrito.py first")
        return 1
    bs = blocos(fonte.read_text())
    por_titulo = {t: c for t, c in bs}

    for exigido in ("Title", "Highlights", "Abstract", "Keywords",
                    "Figure captions", "Table 1"):
        if exigido not in por_titulo:
            print(f"19_tex: the manuscript has no '## {exigido}' block. "
                  f"Refusing to emit a document that silently lacks it.")
            return 1

    def junta(linhas: list[str]) -> str:
        """Join a one-paragraph block, dropping the Markdown horizontal rule
        that separates it from the next. The first build took that rule for
        part of the title and printed it as '... Than the Data ---'."""
        return " ".join(x.strip() for x in linhas
                        if x.strip() and x.strip() != "---")

    titulo = junta(por_titulo["Title"])
    out: list[str] = [PREAMBULO]
    out.append("\\title{" + inline(titulo, onde="title") + "}")
    # \author sets its argument in an unbreakable box, so the placeholder has
    # to carry its own \parbox: the first build ran it 734pt off the page.
    # The title page, from the manuscript when it carries one. The author
    # supplied the names, affiliations, corresponding author and ORCIDs on
    # 2026-11-10; before that this printed a visible marker naming what was
    # missing, and that marker stays for a manuscript that still has none.
    # The converter reads which of the two is true instead of being told.
    if "Authors" in por_titulo and por_titulo["Authors"]:
        # Paragraphs, not lines. The first build broke every affiliation at
        # the draft's own 79-column wrap, so "Barao" and "Geraldo" landed on
        # different lines of the title page. A blank line is a break; a line
        # ending is not.
        paragrafos, atual = [], []
        for linha in por_titulo["Authors"]:
            if set(linha.strip()) == {"-"} and len(linha.strip()) >= 3:
                # A Markdown horizontal rule separates the emitted blocks and
                # is not content -- the same rule that once printed a dash at
                # the end of Figure 5's caption.
                continue
            if linha.strip():
                atual.append(linha.strip())
            elif atual:
                paragrafos.append(" ".join(atual)); atual = []
        if atual:
            paragrafos.append(" ".join(atual))

        # ^x^ is superscript, and it is converted HERE and nowhere else. The
        # drafts hold two lone carets -- q^2/L and 10^-6 -- which are
        # exponents in running text and must keep escaping as they do; a
        # global rule would be a rule that has to know the difference.
        ALVO = "\x00SUP\x00"

        def _supers(texto: str) -> str:
            guardados = []

            def _tira(m):
                guardados.append(m.group(1))
                return ALVO
            bruto = re.sub(r"\^([^\s^]+)\^", _tira, texto)
            escapado = inline(bruto, onde="Authors")
            for g in guardados:
                escapado = escapado.replace(
                    ALVO, "\\textsuperscript{" + inline(g, onde="Authors")
                    + "}", 1)
            return escapado

        out.append("\\author{\\normalsize")
        out.append("  \\parbox{0.9\\textwidth}{\\centering")
        for i, par in enumerate(paragrafos):
            if i:
                out.append("  \\\\[0.4em]")
            out.append("  " + _supers(par))
        out.append("  }}")
    else:
        out.append(r"""\author{\normalsize\itshape
  \parbox{0.85\textwidth}{\centering
  [Title page pending: the guide requires each author's given and family
  names, affiliations with full postal address and country, and the
  corresponding author's email address. Those are facts this converter does
  not have, and it does not invent them.]}}""")
    out.append("\\date{}")
    out.append("\\begin{document}")
    out.append("\\maketitle")

    # front matter, in the manuscript's own order
    out.append("\\section*{Highlights}")
    out += corpo_para_tex(por_titulo["Highlights"], onde="Highlights")
    out.append("\\begin{abstract}")
    out += corpo_para_tex(por_titulo["Abstract"], onde="Abstract")
    out.append("\\end{abstract}")
    chaves = junta(por_titulo["Keywords"])
    out.append("\\noindent\\textbf{Keywords:} "
               + inline(chaves, onde="Keywords"))
    out.append("")

    # numbered sections, in the order the manuscript emits them
    secoes = [(t, c) for t, c in bs if re.match(r"^\d+\.\s", t)]
    numeros = [int(re.match(r"^(\d+)\.", t).group(1)) for t, _ in secoes]
    if numeros != list(range(1, len(numeros) + 1)):
        print(f"19_tex: sections are not contiguous from 1: {numeros}")
        return 1
    desencontros = confere_numeracao(secoes)
    if desencontros:
        print("19_tex: the numbers LaTeX will print are not the numbers the "
              "manuscript wrote, so every cross-reference after the first "
              "mismatch points at the wrong place:")
        for d in desencontros:
            print(f"    {d}")
        return 1
    for t, c in secoes:
        out.append("\\section{" + inline(re.sub(r"^\d+\.\s*", "", t),
                                         onde=t) + "}")
        out += corpo_para_tex(c, onde=t)

    # The CRediT statement, if the manuscript carries one. It follows the last
    # numbered section, which is where Elsevier puts it -- after the
    # conclusions. In this layout the figures and Table 1 are hoisted to the
    # end, so it precedes them and the references rather than sitting between
    # Table 1 and the list. Emitted only when present: a converter that
    # printed an empty heading would be asserting a statement the manuscript
    # does not make.
    if ("CRediT authorship contribution statement" in por_titulo
            and por_titulo["CRediT authorship contribution statement"]):
        out.append("\\section*{CRediT authorship contribution statement}")
        out += corpo_para_tex(
            por_titulo["CRediT authorship contribution statement"],
            onde="CRediT authorship contribution statement")

    # figures: the caption text is the manuscript's, the graphic is the file
    out.append("\\clearpage")
    out.append("\\section*{Figures}")
    for t, c in bs:
        m = re.match(r"^Figure (\d+)$", t)
        if not m:
            continue
        k = int(m.group(1))
        # "---" is the Markdown rule that separates the caption blocks, not
        # caption text. It rode into Figure 5's caption and printed as a dash
        # at the end of it, which the referee of 2026-11-02 saw as a residual
        # character.
        texto = " ".join(re.sub(r"^\s*>\s?", "", x).strip() for x in c
                         if x.strip() and x.strip() not in (">", "---"))
        arquivo = FIGURAS.get(k)
        out.append("\\begin{figure}[htbp]\\centering")
        seguro = arquivo.replace("_", "\\_")
        out.append("\\IfFileExists{%s}{\\figuranatural{%s}}"
                   "{\\semfigura{%s}}" % (arquivo, arquivo, seguro))
        out.append("\\caption{" + inline(texto, onde=t) + "}")
        out.append("\\end{figure}")
    out.append("\\clearpage")

    # Table 1, as it stands
    out.append("\\section*{Table 1}")
    out.append("% Emitted as it stands. The "
               "translation\n% waits for the author in paper/13-tabela1.md; a "
               "converter is not the place\n% to decide it.")
    out += corpo_para_tex(por_titulo["Table 1"], onde="Table 1")

    # The AI declaration, immediately above the references, which is where
    # Elsevier's policy puts it -- read at the source on 2026-11-11. It is
    # emitted here, after Table 1 and before either bibliography path, so the
    # placement holds in both --bib and the typed list. Emitted only when the
    # manuscript carries one: a heading with nothing under it would be a
    # declaration the authors did not make.
    decl_ia = ("Declaration of Generative AI and AI-assisted technologies "
               "in the writing process")
    if por_titulo.get(decl_ia):
        out.append("\\section*{" + decl_ia + "}")
        out += corpo_para_tex(por_titulo[decl_ia], onde=decl_ia)

    # Data availability, which Elsevier requires, beside the declarations and
    # before the references. Emitted only when present, for the same reason as
    # the declaration above: a heading with nothing under it would be a
    # statement the authors did not make.
    if por_titulo.get("Data availability"):
        out.append("\\section*{Data availability}")
        out += corpo_para_tex(por_titulo["Data availability"],
                              onde="Data availability")

    if a.bib:
        # The journal's chain wants \cite{} and a .bib. The typed list is
        # skipped here: emitting both would print the bibliography twice and
        # let the two drift apart.
        out.append("\\clearpage")
        out.append("\\bibliographystyle{unsrt}")
        out.append("\\bibliography{referencias}")
        out.append("\\end{document}")
        destino = Path(a.out).expanduser()
        corpo = "\n".join(out).rstrip() + "\n"

        mapa = mapa_citacoes()
        if len(mapa) != 21:
            print(f"19_tex --bib: the number-to-key table has {len(mapa)} "
                  "rows, not 21. Refusing to guess the rest.")
            return 1

        faltando: set[str] = set()

        def citar(m: "re.Match[str]") -> str:
            numeros = [x.strip() for x in m.group(1).split(",")]
            chaves = []
            for num in numeros:
                if num not in mapa:
                    faltando.add(num)
                    return m.group(0)
                chaves.append(mapa[num])
            return "\\cite{" + ",".join(chaves) + "}"

        # ONLY after \begin{document}. The preamble writes macro argument
        # counts the same way -- \newcolumntype{P}[1]{...},
        # \providecommand{\semfigura}[1]{...} -- and substituting there turns
        # an argument count into a citation, which destroyed the definitions
        # and produced 46 LaTeX errors on the first attempt at this.
        marca = "\\begin{document}"
        corte = corpo.index(marca) + len(marca)
        cabeca, miolo = corpo[:corte], corpo[corte:]

        # Grouped markers exist ([10,11]), so the pattern takes a list. Only
        # digits and commas: a bracket holding anything else is not a
        # citation and is left alone.
        miolo, n_sub = re.subn(r"\[(\d+(?:\s*,\s*\d+)*)\]", citar, miolo)
        corpo = cabeca + miolo
        if faltando:
            print("19_tex --bib: markers with no key in the table: "
                  + ", ".join(f"[{x}]" for x in sorted(faltando, key=int))
                  + ". Refusing to emit a document that cites nothing.")
            return 1
        restantes = re.findall(r"\[\d+(?:\s*,\s*\d+)*\]", miolo)
        if restantes:
            print(f"19_tex --bib: {len(restantes)} markers survived the "
                  f"substitution: {restantes[:5]}. Refusing.")
            return 1
        destino.write_text(corpo)

        # the submission .bib, beside the .tex, with the provenance notes out
        origem_bib = RAIZ / "paper" / "referencias.bib"
        n_bib = bib_para_submissao(origem_bib, destino.parent / "referencias.bib")
        if not n_bib:
            return 1
        print(f"{destino}: {n_sub} markers -> \\cite{{}}; "
              f"referencias.bib written beside it with {n_bib} entries and "
              "the provenance notes stripped")
        return 0

    out.append("\\clearpage")
    out.append("\\section*{References}")
    # The list is emitted when the consolidated manuscript carries one, and
    # the honest placeholder stays for when it does not. Until 2026-11-09 the
    # manuscript had no references at all and this block said so; saying so
    # was right then and would be a lie now, so the converter reads which of
    # the two is true instead of being told.
    if "References" in por_titulo and por_titulo["References"]:
        # Ragged right, for the reason Table 1 is: a reference line holds a
        # DOI and a journal name that cannot hyphenate, so justification
        # stretches the interword space instead -- visibly so in the entries
        # whose URL is long. Reference lists are conventionally set ragged
        # right for exactly this, and nothing about the records changes.
        out.append("\\begingroup\\raggedright")
        out.append("\\begin{enumerate}[leftmargin=2.2em, label={[\\arabic*]}]")
        for linha in por_titulo["References"]:
            linha = linha.strip()
            if not linha:
                continue
            if set(linha) == {"-"} and len(linha) >= 3:
                # A Markdown horizontal rule separates the emitted blocks and
                # is not content. The same rule once reached Figure 5's
                # caption and printed a dash in the PDF.
                continue
            m = re.match(r"^\[(\d+)\]\s+(.*)$", linha)
            if m is None:
                raise SystemExit(
                    "References: a line that is not '[n] ...' reached the "
                    f"converter: {linha[:70]!r}")
            out.append("\\item " + inline(m.group(2), onde="References"))
        out.append("\\end{enumerate}")
        out.append("\\endgroup")
    else:
        out.append(r"""\noindent\emph{The manuscript has no reference list yet.
This is the state of the manuscript and not an omission of the conversion:
the places that require a citation are audited one by one in
\texttt{paper/12-referencias.md}, with the bibliographic records that are
closed and the ones that await the authors.}""")
    out.append("\\end{document}")

    destino = Path(a.out).expanduser()
    destino.write_text("\n".join(out).rstrip() + "\n")
    bruto = destino.read_text()
    nao_ascii = sorted({c for c in bruto if ord(c) > 127} - set(ACENTOS))
    print(f"  written: {destino}")
    print(f"  {len(bruto.splitlines())} lines, {len(secoes)} numbered "
          f"sections, {sum(1 for t, _ in bs if re.match(r'^Figure \d+$', t))} "
          f"figures")
    print(f"  title: {titulo}")
    print(f"  non-ASCII left outside the accented-Latin set: "
          f"{nao_ascii or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
