#!/usr/bin/env python
"""Assemble the drafts into one manuscript, and report what it left out.

WHY
---
The sections were written in five files, each with Portuguese drafting
apparatus around the English text: notes on what changed, questions for the
author, conformance checks against the ADRs. A reader reviewing the manuscript
as a whole needs the manuscript, in order, without that apparatus -- and needs
to know exactly what was removed, or the consolidation becomes a place where
content can disappear unnoticed.

So this script does two things and prints both:

  1. It writes paper/MANUSCRITO.md from the drafts in the declared order.
  2. It reports every block it dropped, with its file and line count, and
     every section-numbering gap it found.

It is a build step, not an edit: the drafts remain the source, and running it
again after any change regenerates the whole document. Nothing is rewritten,
reordered inside a section, or paraphrased -- the English text is copied
verbatim, so the consolidated file cannot say anything the drafts do not.

THE SECTION 5 GAP, AND HOW IT WAS CLOSED
----------------------------------------
On its first run this script reported the sections as 1, 2, 3, 4, 6, 7, 8, 9,
10, 11: the plan in `00-estrutura.md` had a Section 5 and the drafts carried
that material as Section 4.3. The author settled it on 2026-10-28 by promoting
it to a section of its own (`08-rascunho-s5.md`), keeping the tie-breaking
consequences in Section 4 so that Section 5 is not a repetition of it. The gap
check below stays in place: it is cheap, and the next renumbering will need
it too.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/15_consolidar_manuscrito.py
    python scripts/15_consolidar_manuscrito.py --out paper/MANUSCRITO.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SEP = "=" * 78

# The declared order. Each entry: source file, and which top-level blocks of it
# belong to the manuscript. A block is a "## " heading and everything under it
# until the next "## ". Anything not listed is dropped and reported.
ORDEM: list[tuple[str, list[str]]] = [
    ("02-resumo-C.md", ["__PROSA__"]),
    ("03-rascunho-s1-s2-s3.md", ["1. Introduction", "2. Data and methods",
                                 "3. Results — the two roles of the prior"]),
    ("01-rascunho-resumo-e-s4.md", ["4. What the top-decile overlap measures"]),
    ("08-rascunho-s5.md", ["5. Results — the response to sample size"]),
    ("04-rascunho-s6-s7-s8.md", ["6. Results — the prior controls",
                                 "7. Results — the Raman control",
                                 "8. Results — where the alignment is"]),
    ("05-rascunho-s9-s10-s11.md", ["9. Discussion", "10. Limitations",
                                   "11. Future work"]),
    ("09-rascunho-s12.md", ["12. Conclusions"]),
]
# The manuscript must carry twelve contiguous sections. Section 12 was created
# by the integral audit of 2026-10-28; before it the paper ended at Future
# work and had no conclusion at all. The gap check below enforces contiguity,
# and this constant makes the expected count explicit rather than implied.
SECOES_ESPERADAS = 12
LEGENDAS = "06-legendas-figuras.md"
ESTRUTURA = "00-estrutura.md"


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def blocos(texto: str) -> list[tuple[str, str]]:
    """Split on top-level '## ' headings. Returns (title, body including the
    heading). Text before the first heading is returned under '__PROSA__'."""
    partes = re.split(r"^## ", texto, flags=re.M)
    saida = [("__PROSA__", partes[0])]
    for p in partes[1:]:
        titulo = p.split("\n", 1)[0].strip()
        saida.append((titulo, "## " + p))
    return saida


def prosa_do_resumo(texto: str) -> str:
    """The abstract file opens with commented decision history. Keep only the
    prose paragraphs -- lines that are not headings, comments, metadata or
    list items -- and REFUSE if more than one substantial block survives.

    The earlier version took the longest block. On 2026-10-28 the abstract
    was rewritten with a line beginning "-- leaves the prior's ...", which
    this filter read as a list bullet; the paragraph split in two and the
    longest block was a 228-word fragment missing its first two sentences.
    The generator reported 228 words and emitted the truncated abstract
    without complaint. A heuristic that silently ships a shortened abstract
    is worse than one that stops, so this stops.

    A list marker is a hyphen followed by a space. "--" mid-prose is not one.
    """
    manter, atual = [], []
    for linha in texto.splitlines():
        s = linha.strip()
        lista = (re.match(r"^[-*] ", s) or s in ("-", "*")
                 or re.match(r"^\d+[.)] ", s))
        if (not s or lista or s.startswith(("#", ">", "|", "Data:",
                                            "Registro:", "Status:"))):
            if atual:
                manter.append(" ".join(atual))
                atual = []
            continue
        atual.append(s)
    if atual:
        manter.append(" ".join(atual))
    grandes = [b for b in manter if len(b.split()) >= 40]
    if len(grandes) > 1:
        raise SystemExit(
            "the abstract file yields " + str(len(grandes)) + " prose blocks "
            "of 40+ words:\n  " + "\n  ".join(
                f"{len(b.split())} words: {b[:60]}..." for b in grandes)
            + "\nThe abstract must be one block. Taking the longest would "
              "ship a truncated\nabstract and report its word count as the "
              "abstract's. Join the paragraph, or\ncheck for a line that "
              "looks like a list item to this filter.")
    if not grandes:
        return max(manter, key=len) if manter else ""
    return grandes[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="paper")
    ap.add_argument("--out", default="paper/MANUSCRITO.md")
    a = ap.parse_args()
    d = Path(a.dir).expanduser()

    head("Consolidating the manuscript")
    pecas: list[str] = []
    descartados: list[tuple[str, str, int]] = []
    secoes_vistas: list[int] = []

    for nome, queridos in ORDEM:
        p = d / nome
        if not p.is_file():
            raise SystemExit(f"missing source: {p}")
        texto = p.read_text()
        bs = blocos(texto)
        achados = {t for t, _ in bs}
        for q in queridos:
            if q not in achados:
                raise SystemExit(
                    f"{nome}: expected block '## {q}' and it is not there. "
                    f"Found: {sorted(x for x in achados if x != '__PROSA__')}. "
                    f"Fix ORDEM or the draft rather than emitting a "
                    f"manuscript with a hole in it.")
        for titulo, corpo in bs:
            if titulo in queridos:
                if titulo == "__PROSA__" and nome.startswith("02"):
                    resumo = prosa_do_resumo(corpo)
                    if not resumo:
                        raise SystemExit(f"{nome}: no abstract prose found")
                    pecas.append("## Abstract\n\n" + resumo + "\n")
                    print(f"  {nome:<30} abstract, "
                          f"{len(resumo.split())} words")
                else:
                    pecas.append(corpo.rstrip() + "\n")
                    m = re.match(r"(\d+)\.", titulo)
                    if m:
                        secoes_vistas.append(int(m.group(1)))
                    print(f"  {nome:<30} ## {titulo[:44]:<44} "
                          f"{len(corpo.splitlines())} lines")
            else:
                if titulo == "__PROSA__" and not corpo.strip():
                    continue
                descartados.append((nome, titulo, len(corpo.splitlines())))

    # captions, verbatim
    pl = d / LEGENDAS
    bs = blocos(pl.read_text())
    legendas = [c for t, c in bs if t.startswith("Figura")]
    if len(legendas) != 5:
        raise SystemExit(f"{LEGENDAS}: expected 5 figure blocks, found "
                         f"{len(legendas)}")
    pecas.append("## Figure captions\n\n" + "\n".join(
        c.rstrip() + "\n" for c in legendas))
    print(f"  {LEGENDAS:<30} 5 captions")
    for t, c in bs:
        if not t.startswith("Figura") and t != "__PROSA__":
            descartados.append((LEGENDAS, t, len(c.splitlines())))

    # Table 1, from the structure document, verbatim. Anchored on its own
    # header: an earlier version of this script matched the first table whose
    # cells happened to contain the word "critério" and silently emitted a
    # table of parameters as Table 1. A consolidation that can ship the wrong
    # table is worse than one that ships none.
    est = (d / ESTRUTURA).read_text()
    CAB = ("| | enunciado | veredito pelo critério | o que o resultado "
           "sustenta |")
    if CAB not in est:
        raise SystemExit(
            f"{ESTRUTURA}: Table 1's header is not there as expected:\n"
            f"  {CAB}\nIt was renamed or reworded. Fix this script's anchor "
            f"rather than letting it match whichever table comes first.")
    inicio = est.index(CAB)
    linhas = []
    for linha in est[inicio:].splitlines():
        if linha.startswith("|"):
            linhas.append(linha)
        elif linhas:
            break
    tabela = "\n".join(linhas)
    pecas.append("## Table 1\n\n" + tabela + "\n")
    hipoteses = sum(1 for x in linhas if re.match(r"\| *\**H\d", x))
    print(f"  {ESTRUTURA:<30} Table 1, {len(linhas)} rows, "
          f"{hipoteses} hypotheses")

    saida = Path(a.out).expanduser()
    # Provenance in the file itself, but DETERMINISTIC. An earlier version put
    # the git revision and a count of uncommitted files in this header, which
    # made the generated file depend on the working tree: two machines at the
    # same sources produced different bytes, a patch carrying this file could
    # not apply anywhere but where it was built, and that is exactly how the
    # delivery of 2026-10-28 failed. The digest below is over the SOURCES, so
    # it identifies the content that was consolidated and nothing else.
    import hashlib
    h = hashlib.sha256()
    fontes = [n for n, _ in ORDEM] + [LEGENDAS, ESTRUTURA]
    for n in fontes:
        h.update((d / n).read_bytes())
    digest = h.hexdigest()[:16]
    cabeca = ("# Manuscript, consolidated\n\n"
              "Generated by `scripts/15_consolidar_manuscrito.py` from the "
              "drafts in `paper/`.\nThe English text is copied verbatim; the "
              "Portuguese drafting apparatus is\nleft behind and listed at "
              "the end of the generator's output. Do not edit this\nfile -- "
              "edit the drafts and run the generator again.\n\n"
              f"Source digest: **{digest}** — SHA-256 over the "
              f"{len(fontes)} draft files this was\nbuilt from, truncated. "
              f"Two copies with the same digest were built from the same\n"
              f"sources, whatever the git state. The findings in `findings/` "
              f"and Table 1 below\nbelong with this digest; the generator "
              f"prints the git revision alongside it.\n\n---\n\n")
    saida.write_text(cabeca + "\n---\n\n".join(pecas))
    palavras = len(saida.read_text().split())
    print(f"\n  written: {saida}   {palavras} words, "
          f"{len(saida.read_text().splitlines())} lines")
    print(f"  source digest {digest}")
    # The git state goes to stdout, where it informs the person running the
    # build without contaminating the artefact.
    try:
        import subprocess
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        sujo = subprocess.run(["git", "status", "--porcelain"],
                              capture_output=True, text=True).stdout.strip()
        print(f"  git: {rev or '?'}"
              + (f", {len(sujo.splitlines())} file(s) uncommitted -- commit "
                 f"before quoting this build as a state" if sujo else
                 ", clean working tree"))
    except Exception:
        print("  git: state unavailable")

    head("What was left out, so that nothing disappears quietly")
    if not descartados:
        print("  nothing")
    for nome, titulo, n in descartados:
        print(f"  {nome:<30} ## {titulo[:40]:<40} {n:>4} lines")

    # A dropped block named Abstract is not ordinary apparatus: it means two
    # abstracts exist and one of them was not used. Which one is in the
    # manuscript has to be stated, not inferred from the ORDEM table.
    outros = [x for x in descartados if x[1].strip().lower() == "abstract"]
    if outros:
        print()
        print("  TWO ABSTRACTS EXIST. The manuscript carries the one from "
              "02-resumo-C.md,\n  the register-C version approved on "
              "2026-10-24. The block dropped here is")
        for nome, _, n in outros:
            print(f"    {nome}, {n} lines -- the earlier draft, superseded")
        print("  If that is the wrong way round, this script's ORDEM table "
              "is where to fix\n  it; the drafts are not the place to "
              "resolve it by deletion.")

    head("Section numbering")
    print(f"  sections emitted: {secoes_vistas}")
    faltando = [n for n in range(1, max(SECOES_ESPERADAS,
                                        max(secoes_vistas) + 1))
                if n not in secoes_vistas] if secoes_vistas else []
    faltando = [n for n in faltando if n <= max(SECOES_ESPERADAS,
                                                max(secoes_vistas))]
    if faltando:
        print(f"  GAP: {faltando}")
        print("  A section number in the plan has no draft block, or a block "
              "was moved and\n  not renumbered. The consolidated file is "
              "emitted with the gap rather than\n  with a number invented to "
              "fill it: which section is missing is the\n  author's to "
              "settle, not this script's.")
    else:
        print("  contiguous")


if __name__ == "__main__":
    main()
