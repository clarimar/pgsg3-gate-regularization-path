"""The chance level for a tied block, and what the program used to call exact.

Calibrated by measured quantities, not arbitrary scales: the fixture reproduces
the real plateau geometry (L=34) and both decile conventions (q=28, 29), and the
asserted values are those recomputed from the archived gates. The earlier
failure in this program came from a fixture perturbed at sd=1e-2 when the data
sat at 1.5e-4 -- 70x off -- which made a real finding look refuted.
"""
from __future__ import annotations

import importlib.util
from math import comb
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]


def _mod():
    cam = RAIZ / "scripts" / "check_gates_r2.py"
    esp = importlib.util.spec_from_file_location("cgr2", cam)
    m = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m)
    return m


@pytest.mark.parametrize("q,esperado", [(28, 0.701177), (29, 0.744473)])
def test_esperanca_exata(q, esperado):
    assert _mod().jaccard_esperado_exato(q, 34) == pytest.approx(esperado,
                                                                abs=1e-6)


@pytest.mark.parametrize("q", [28, 29])
def test_aproximacao_e_limite_inferior_estrito(q):
    """q/(2L-q) is J(E[k]), and J is strictly convex, so Jensen is strict."""
    L = 34
    exato = _mod().jaccard_esperado_exato(q, L)
    aprox = q / (2 * L - q)
    assert aprox < exato
    # the ratio IS J evaluated at the hypergeometric mean overlap
    Ek = q * q / L
    assert Ek / (2 * q - Ek) == pytest.approx(aprox, abs=1e-12)


@pytest.mark.parametrize("q", [28, 29])
def test_exata_bate_com_monte_carlo(q):
    """Independent route to the same number: draw the subsets."""
    L, rng = 34, np.random.default_rng(0)
    v = [len(a & b) / len(a | b)
         for a, b in ((set(rng.choice(L, q, replace=False).tolist()),
                       set(rng.choice(L, q, replace=False).tolist()))
                      for _ in range(40000))]
    assert np.mean(v) == pytest.approx(_mod().jaccard_esperado_exato(q, L),
                                       abs=3e-4)


def test_hipergeometrica_soma_um():
    q, L = 29, 34
    tot = comb(L, q)
    s = sum(comb(q, k) * comb(L - q, q - k) / tot
            for k in range(max(0, 2 * q - L), q + 1))
    assert s == pytest.approx(1.0, abs=1e-12)


def test_o_script_nao_chama_a_aproximacao_de_acaso():
    """Guarded on the script, not on the notes: a dated note may quote a
    retired claim in order to retract it, and a live assertion may not.
    test_analise_condicional owns the same guard for the 10/10 count."""
    fonte = (RAIZ / "scripts" / "check_gates_r2.py").read_text()
    assert "chance 0.7436 against 0.7000" not in fonte
    assert "E[J] exact" in fonte and "q/(2L-q)" in fonte


def test_correcoes_datadas_presentes():
    """Each retracted claim keeps its original text plus a dated note."""
    f004 = (RAIZ / "findings"
            / "F004-estabilidade-interpretativa-e-funcao-dos-dados.md").read_text()
    # original text preserved
    assert "coincidem até" in f004
    # and corrected
    assert "Correção de 2026-10-24 — dois erros meus nesta nota" in f004
    assert "livre de empate a partir de n = 200" in f004
    f002 = (RAIZ / "findings"
            / "F002-o-que-as-metricas-interpretativas-medem.md").read_text()
    assert "0,701177" in f002 and "Jensen" in f002


def test_rascunho_nao_afirma_ausencia_total_de_empate():
    """The draft said the unanchored arm has no ties and the two rules agree
    to the last digit. True from n = 200, false below it. Corrected
    2026-10-24; the absolute phrasing must not come back."""
    t = (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text()
    assert "where no ties occur" not in t
    assert "From n = 200 upward it carries no ties at all" in t
    assert "two orders of magnitude below" in t


def test_rascunho_usa_a_esperanca_exata():
    t = (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text()
    assert "0.7012" in t and "0.7445" in t
    assert "strictly\nconvex" in t or "strictly convex" in t
    assert "0.7442" in t          # the measured q=29 collapse, no longer pending
    assert "PENDENTE" not in t


def test_cruzamento_acusa_convencao_divergente(tmp_path):
    """The guard that would have caught the mirrored error: in F004 I flagged
    ADR-0001's Jaccard range as divergent when the range was correct and my
    script had truncated q to 28 while the record declares 29. The script now
    reads the record's own q and must say CONVENTION, not DIVERGENCE."""
    import itertools
    import subprocess
    import sys

    p, L, rng = 281, 34, np.random.default_rng(0)
    prior = np.concatenate([np.full(223, 0.1), np.full(7, 0.6),
                            np.full(17, 0.8), np.full(L, 1.0)])
    plato = np.flatnonzero(prior >= 1.0 - 1e-9)
    g = np.repeat(np.clip(prior * 0.98, 1e-6, 1 - 1e-6)[None, :], 10, axis=0)
    g = np.clip(g + rng.normal(0, 1.5e-4, g.shape), 0.0, 1.0)
    g[:, plato] = 1.0 - 1e-6                       # bit-identical, as measured
    np.savez(tmp_path / "gates_n30.npz", gates_lit=g, prior=prior,
             wavelengths=np.linspace(1100.0, 2300.0, p))

    def jm(q):
        tops = [set(np.argsort(x)[::-1][:q].tolist()) for x in g]
        return float(np.mean([len(a & b) / len(a | b)
                              for a, b in itertools.combinations(tops, 2)]))

    (tmp_path / "gate_metrics.csv").write_text(
        "n_actual,p,q,jaccard_lit\n" f"30,{p},29,{jm(29):.6f}\n")

    def correr(*extra):
        return subprocess.run(
            [sys.executable, str(RAIZ / "scripts" / "check_gates_r2.py"),
             "--dir", str(tmp_path), *extra],
            capture_output=True, text=True, check=True).stdout

    def marcas(saida: str) -> list[str]:
        """The flags on the data lines only -- the legend names them too."""
        return [ln.split()[-1] for ln in saida.splitlines()
                if "jaccard_lit" in ln and "stored " in ln and "here " in ln]

    assert marcas(correr()) == ["ok"]
    # pinned to the other convention: flagged as incomparable, not as a
    # disagreement about the measurement
    assert marcas(correr("--q", "28")) == ["CONVENTION"]
