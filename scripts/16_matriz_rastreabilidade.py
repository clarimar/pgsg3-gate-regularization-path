#!/usr/bin/env python
"""Which decision does each test protect, and which decisions have no test?

WHY
---
The author's recommendation of 2026-10-28: keep a traceability matrix from
scientific decision to source file to automated test to evidence, and
distinguish three kinds of test.

  numeric     metrics, counts, measured results
  structural  sections, extraction, consolidation, file integrity
  semantic    scientific commitments -- the q = 28 against q = 29 distinction,
              the post hoc status of the tie-breaking analysis, the four
              requirements attached to approving register C

The third kind earned its place twice in one afternoon. The register-C test
caught a compression that had deleted two of the author's binding
requirements from the abstract, and the consolidator's guard caught an
abstract silently truncated to 228 words. Neither was a numeric error.

WHAT THIS IS NOT
----------------
A semantic test checks that a commitment is still *stated*. A sentence can
satisfy a substring search and still carry a wrong interpretation, so these
tests are regression barriers against defects already seen, not a substitute
for reading. The matrix says which decisions are guarded; it does not say the
guarded ones are correct.

HOW A TEST DECLARES ITSELF
--------------------------
By a pytest marker: @pytest.mark.semantico, .estrutural or .numerico. Nothing
is inferred from a test's name or its assertions -- a matrix built by guessing
would be a matrix that quietly misclassifies. Tests without a marker are
listed as UNCLASSIFIED, with their count, so the gap is visible rather than
filled in.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/16_matriz_rastreabilidade.py
    python scripts/16_matriz_rastreabilidade.py --md docs/matriz.md
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

SEP = "=" * 78
CATEGORIAS = ("semantico", "estrutural", "numerico")


def head(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def marcadores(no: ast.FunctionDef) -> list[str]:
    saida = []
    for d in no.decorator_list:
        alvo = d.func if isinstance(d, ast.Call) else d
        partes = []
        while isinstance(alvo, ast.Attribute):
            partes.append(alvo.attr)
            alvo = alvo.value
        if isinstance(alvo, ast.Name):
            partes.append(alvo.id)
        nome = list(reversed(partes))
        if len(nome) >= 3 and nome[0] == "pytest" and nome[1] == "mark":
            saida.append(nome[2])
    return saida


def primeira_linha(doc: str | None) -> str:
    if not doc:
        return ""
    for linha in doc.strip().splitlines():
        if linha.strip():
            return linha.strip()
    return ""


def fontes_citadas(no: ast.FunctionDef, texto: str) -> list[str]:
    """Which repository files the test reads. Taken from the literals in the
    test body, not from its name."""
    seg = ast.get_source_segment(texto, no) or ""
    achados = set()
    for m in re.finditer(r'"([-\w./]+\.(?:md|py|toml|csv|json|npz))"', seg):
        achados.add(m.group(1))
    for m in re.finditer(r'"(F\d{3}[-\w]*\.md)"', seg):
        achados.add(m.group(1))
    return sorted(achados)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="tests")
    ap.add_argument("--md", default="")
    a = ap.parse_args()

    arquivos = sorted(Path(a.dir).expanduser().glob("test_*.py"))
    if not arquivos:
        raise SystemExit(f"no test_*.py in {a.dir}")

    registros = []
    for p in arquivos:
        texto = p.read_text()
        arvore = ast.parse(texto)
        for no in arvore.body:
            if not (isinstance(no, ast.FunctionDef)
                    and no.name.startswith("test_")):
                continue
            marcas = [m for m in marcadores(no) if m in CATEGORIAS]
            registros.append({
                "arquivo": p.name,
                "teste": no.name,
                "categoria": marcas[0] if marcas else "UNCLASSIFIED",
                "decisao": primeira_linha(ast.get_docstring(no)),
                "fontes": fontes_citadas(no, texto),
            })

    head("Traceability matrix: decision -> source -> test")
    print(f"  {len(registros)} tests in {len(arquivos)} files")
    for c in CATEGORIAS + ("UNCLASSIFIED",):
        n = sum(1 for r in registros if r["categoria"] == c)
        print(f"    {c:<14} {n:>4}")

    for c in CATEGORIAS:
        marcados = [r for r in registros if r["categoria"] == c]
        if not marcados:
            continue
        head(f"{c} ({len(marcados)})")
        for r in marcados:
            print(f"  {r['teste']}")
            if r["decisao"]:
                print(f"      decision: {r['decisao'][:68]}")
            if r["fontes"]:
                print(f"      guards:   {', '.join(r['fontes'][:4])}")

    naoclass = [r for r in registros if r["categoria"] == "UNCLASSIFIED"]
    head(f"Unclassified ({len(naoclass)})")
    print("  These carry no marker. They are not assumed to be numeric: the")
    print("  category is declared, never inferred, because a matrix built by")
    print("  guessing would misclassify quietly. Classify them by adding")
    print("  @pytest.mark.numerico, .estrutural or .semantico.")
    print()
    por_arquivo: dict[str, int] = {}
    for r in naoclass:
        por_arquivo[r["arquivo"]] = por_arquivo.get(r["arquivo"], 0) + 1
    for k in sorted(por_arquivo):
        print(f"    {k:<34} {por_arquivo[k]:>4}")

    head("What the matrix does not establish")
    print("  A semantic test checks that a commitment is still STATED. A")
    print("  sentence can satisfy a substring search and still carry a wrong")
    print("  interpretation. These are regression barriers against defects")
    print("  already seen -- not a substitute for reading the manuscript.")

    if a.md:
        saida = Path(a.md).expanduser()
        saida.parent.mkdir(parents=True, exist_ok=True)
        linhas = ["# Matriz de rastreabilidade", "",
                  "Gerado por `scripts/16_matriz_rastreabilidade.py`. Não "
                  "editar: a categoria de cada", "teste é declarada no "
                  "próprio teste, por marcador `pytest`.", "",
                  f"{len(registros)} testes em {len(arquivos)} arquivos.", ""]
        for c in CATEGORIAS + ("UNCLASSIFIED",):
            m = [r for r in registros if r["categoria"] == c]
            linhas += [f"## {c} ({len(m)})", ""]
            if c == "UNCLASSIFIED":
                linhas += ["Sem marcador. A categoria não é inferida.", ""]
                for k in sorted({r["arquivo"] for r in m}):
                    n = sum(1 for r in m if r["arquivo"] == k)
                    linhas.append(f"- `{k}` — {n}")
                linhas.append("")
                continue
            linhas += ["| teste | decisão protegida | arquivos |",
                       "| --- | --- | --- |"]
            for r in m:
                f = ", ".join(f"`{x}`" for x in r["fontes"][:3]) or "—"
                linhas.append(f"| `{r['teste']}` | {r['decisao'][:90]} | {f} |")
            linhas.append("")
        # rstrip: a trailing blank line trips `git diff --check`, and a
        # generated file that fails the project's own whitespace check
        # is a generated file that will be committed with a warning.
        saida.write_text("\n".join(linhas).rstrip() + "\n")
        print(f"\n  written: {saida}")


if __name__ == "__main__":
    main()
