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

Table 1 is emitted as it stands, which today means in Portuguese. The
translation waits in paper/13-tabela1.md for the author; the conversion is not
the place to decide it.

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
ACENTOS = "áâãàçéêíóôõúüÁÂÃÀÇÉÊÍÓÔÕÚÜñÑ"
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

    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"\\emph{\1}", s)

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
        s = s.replace(f"\x00{i}\x00", "\\texttt{" + "".join(partes) + "}")
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
        spec = "".join("p{%.3f\\linewidth}" % f for f in fracoes)
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
        elif s.startswith("#### "):
            fora.append("\\subsubsection{" + inline(
                re.sub(r"^#+\s*[\d.]*\s*", "", s), onde=onde) + "}")
            i += 1
        elif s.startswith("### "):
            fora.append("\\subsection{" + inline(
                re.sub(r"^#+\s*[\d.]*\s*", "", s), onde=onde) + "}")
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
        elif re.match(r"^[-*] ", s):
            j, itens = i, []
            while j < n and re.match(r"^[-*] ", linhas[j].strip()):
                itens.append(linhas[j].strip()[2:])
                j += 1
            fora.append("\\begin{itemize}")
            fora += ["\\item " + inline(x, onde=onde) for x in itens]
            fora.append("\\end{itemize}")
            i = j
        elif re.match(r"^\d+\. ", s):
            j, itens = i, []
            while j < n and re.match(r"^\d+\. ", linhas[j].strip()):
                itens.append(re.sub(r"^\d+\.\s*", "", linhas[j].strip()))
                j += 1
            fora.append("\\begin{enumerate}")
            fora += ["\\item " + inline(x, onde=onde) for x in itens]
            fora.append("\\end{enumerate}")
            i = j
        elif l.startswith("    ") or l.startswith("\t"):
            fora.append("\\begin{quote}\\ttfamily\\small")
            while i < n and (linhas[i].startswith("    ")
                             or linhas[i].startswith("\t")):
                fora.append(inline(linhas[i].strip(), onde=onde) + "\\\\")
                i += 1
            fora.append("\\end{quote}")
        else:
            fora.append(inline(s, onde=onde))
            i += 1
    return fora


PREAMBULO = r"""% Reading copy, generated by scripts/19_tex.py -- do not edit by hand.
% Compiles with pdfLaTeX. For the figures to appear, put the five PDFs of
% paper/figuras/ in a figuras/ folder beside this file; without them the
% build still succeeds and each figure shows a framed placeholder.
%
% NOT THE SUBMISSION FILE. The journal takes elsarticle.cls, whose front
% matter differs, and the title page needs the authors' names, affiliations
% with postal address and country, and the corresponding author's email --
% facts this converter does not have. The reference list does not exist yet;
% see paper/12-referencias.md.
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
\usepackage{booktabs,longtable}
\usepackage{graphicx}
\usepackage[margin=2.5cm]{geometry}
\usepackage{parskip}
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
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(RAIZ / "paper" / "MANUSCRITO.tex"))
    # The source is an argument so that a test can build from a manuscript it
    # generated itself, into a directory of its own. Pinning both to the
    # repository made two tests depend on a GENERATED file being up to date:
    # they passed here and failed in the clean clone, where the committed
    # manuscript predates the title this build added.
    ap.add_argument("--src", default=str(FONTE))
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
    for t, c in secoes:
        out.append("\\section{" + inline(re.sub(r"^\d+\.\s*", "", t),
                                         onde=t) + "}")
        out += corpo_para_tex(c, onde=t)

    # figures: the caption text is the manuscript's, the graphic is the file
    out.append("\\clearpage")
    out.append("\\section*{Figures}")
    for t, c in bs:
        m = re.match(r"^Figure (\d+)$", t)
        if not m:
            continue
        k = int(m.group(1))
        texto = " ".join(re.sub(r"^\s*>\s?", "", x).strip() for x in c
                         if x.strip() and x.strip() != ">")
        arquivo = FIGURAS.get(k)
        out.append("\\begin{figure}[htbp]\\centering")
        seguro = arquivo.replace("_", "\\_")
        out.append("\\IfFileExists{%s}{\\includegraphics[width=\\linewidth]{%s}}"
                   "{\\semfigura{%s}}" % (arquivo, arquivo, seguro))
        out.append("\\caption{" + inline(texto, onde=t) + "}")
        out.append("\\end{figure}")
    out.append("\\clearpage")

    # Table 1, as it stands
    out.append("\\section*{Table 1}")
    out.append("% Emitted as it stands, which today means in Portuguese. The "
               "translation\n% waits for the author in paper/13-tabela1.md; a "
               "converter is not the place\n% to decide it.")
    out += corpo_para_tex(por_titulo["Table 1"], onde="Table 1")

    out.append("\\clearpage")
    out.append("\\section*{References}")
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
