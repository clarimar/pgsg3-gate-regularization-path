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
import sys
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


def expansoes(no: ast.FunctionDef) -> int:
    """How many extra collected items a parametrised test produces.

    The matrix counts TEST FUNCTIONS. pytest collects ITEMS, and a
    parametrised function yields one item per case. Reporting a sum of
    functions next to a remembered item count invites the reader to subtract
    them, which is what happened on 2026-10-28: 242 against 257, a difference
    of 15 with no explanation attached. So the difference is computed here,
    from the decorators, rather than asserted.
    """
    total = 0
    for d in no.decorator_list:
        if not isinstance(d, ast.Call):
            continue
        alvo, partes = d.func, []
        while isinstance(alvo, ast.Attribute):
            partes.append(alvo.attr)
            alvo = alvo.value
        if isinstance(alvo, ast.Name):
            partes.append(alvo.id)
        nome = list(reversed(partes))
        if nome[-1:] != ["parametrize"] or len(d.args) < 2:
            continue
        if isinstance(d.args[1], (ast.List, ast.Tuple)):
            total += len(d.args[1].elts) - 1
    return total


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
    ap.add_argument("--md", default="",
                    help="write the matrix to this path")
    ap.add_argument("--collect", action="store_true",
                    help="also run pytest --collect-only and compare the "
                         "static prediction against the real item count")
    ap.add_argument("--check", default="",
                    help="compare this file against what the tests produce "
                         "now; exit non-zero if they differ")
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
                "expansoes": expansoes(no),
                "categoria": marcas[0] if marcas else "UNCLASSIFIED",
                "decisao": primeira_linha(ast.get_docstring(no)),
                "fontes": fontes_citadas(no, texto),
            })

    head("Traceability matrix: decision -> source -> test")
    exp = sum(r["expansoes"] for r in registros)
    print(f"  UNIT OF COUNT: test FUNCTIONS defined at module level, taken "
          f"from the source\n  by AST. Not items collected by pytest, and "
          f"not tests executed.")
    print()
    print(f"  {len(registros):>4}  test functions in {len(arquivos)} files")
    for c in CATEGORIAS + ("UNCLASSIFIED",):
        n = sum(1 for r in registros if r["categoria"] == c)
        print(f"    {n:>4}  {c}")
    print()
    print(f"  STATIC reconciliation -- read from the source, not from a "
          f"pytest run:")
    print(f"    {len(registros):>4}  test functions")
    print(f"    {exp:>+4}  items added by parametrised cases (literal lists "
          f"in the decorators)")
    print(f"    {len(registros) + exp:>4}  items this predicts pytest "
          f"collects")
    print("  It is a prediction and not an equivalent. A static read cannot "
          "see parametrisation\n  built at runtime, parametrised fixtures, "
          "cases generated by hooks, or a module\n  skipped for a missing "
          "dependency. Where the two disagree, pytest's own count is\n  the "
          "authority: run with --collect to have it checked instead of "
          "assumed.")
    if a.collect:
        print()
        import subprocess
        r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                            "--collect-only"], capture_output=True, text=True)
        itens = sum(1 for l in r.stdout.splitlines() if "::" in l)
        print(f"  pytest --collect-only reports {itens} items")
        delta = itens - (len(registros) + exp)
        if delta == 0:
            print("  the static prediction matches exactly")
        else:
            print(f"  DIFFERS from the prediction by {delta:+d}. Causes to "
                  f"look at, in order:\n    a module skipped for a missing "
                  f"dependency (collects fewer), or\n    parametrisation this "
                  f"static read cannot see (collects more).")
            saltados = [l for l in r.stdout.splitlines()
                        if "error" in l.lower() or "skipped" in l.lower()]
            for l in saltados[:4]:
                print(f"    {l.strip()[:90]}")

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

    if a.md or a.check:
        texto_md = montar_md(registros, len(arquivos))
    if a.check:
        alvo = Path(a.check).expanduser()
        head("Check: is the stored matrix the one these tests produce?")
        if not alvo.is_file():
            print(f"  {alvo} does not exist. Generate it with --md.")
            raise SystemExit(1)
        atual = alvo.read_text()
        if atual == texto_md:
            print(f"  {alvo}: in sync with the tests")
            raise SystemExit(0)
        print(f"  {alvo}: OUT OF SYNC with the tests.")
        import difflib
        d = list(difflib.unified_diff(
            atual.splitlines(), texto_md.splitlines(),
            fromfile="stored", tofile="regenerated", lineterm=""))
        print(f"  {sum(1 for x in d if x.startswith(('+', '-')) and not x.startswith(('+++', '---')))} "
              f"differing lines; first few:")
        for linha in d[:14]:
            print("    " + linha[:100])
        print()
        print("  Being generated does not make it synchronised: the tests can "
              "change and the\n  file not be regenerated. Run with --md to "
              "update it.")
        raise SystemExit(1)
    if a.md:
        saida = Path(a.md).expanduser()
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(texto_md)
        print(f"\n  written: {saida}")


def montar_md(registros: list[dict], n_arquivos: int) -> str:
        linhas = ["# Matriz de rastreabilidade", "",
                  "Gerado por `scripts/16_matriz_rastreabilidade.py`. Não "
                  "editar: a categoria de cada", "teste é declarada no "
                  "próprio teste, por marcador `pytest`.", "",
                  f"{len(registros)} funções de teste em {n_arquivos} "
                  f"arquivos. A unidade de contagem é a **função de teste** "
                  f"definida no", "nível do módulo, lida da fonte por AST — "
                  f"não é item coletado pelo pytest nem teste executado. "
                  f"Casos", f"parametrizados somam "
                  f"+{sum(r['expansoes'] for r in registros)} itens na "
                  f"coleta.", ""]
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
        # rstrip: a trailing blank line trips `git diff --check`, and a
        # generated file that fails the project's own whitespace check
        # is a generated file that will be committed with a warning.
        return "\n".join(linhas).rstrip() + "\n"


if __name__ == "__main__":
    main()
