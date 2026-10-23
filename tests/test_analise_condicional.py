"""Tests for `scripts/08_analise_condicional.py` (H13).

What matters most here is the partial-correlation formula: it is the one new
statistic in this round, it has a closed form that is easy to get subtly wrong,
and a sign error in it would invert a verdict. It is therefore checked against
cases whose answer is known independently, not against itself.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
P, NS = 281, 10
PISO = np.arange(0, 223)


def _carregar():
    caminho = RAIZ / "scripts" / "08_analise_condicional.py"
    spec = importlib.util.spec_from_file_location("cond_h13", caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cond_h13"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def prior_degrau() -> np.ndarray:
    pr = np.full(P, 0.1)
    pr[223:230] = 0.6
    pr[230:247] = 0.8
    pr[247:281] = 1.0
    return pr


def escrever(d: Path, prior, gates1, gates0, relevance, arm="literature",
             agree0=None, h=70) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    linhas = []
    for lam, gs in ((0.0, gates0), (1.0, gates1)):
        for s, g in enumerate(gs):
            ag = (agree0[s] if (lam == 0.0 and agree0 is not None)
                  else mod.spearman(g, relevance))
            linhas.append({"lam": lam, "seed": s, "prior_arm": arm,
                           "agree_pls": ag, "r2": 0.8})
    with (d / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    np.savez_compressed(d / "gates.npz", prior=prior, pls_relevance=relevance,
                        pls_h_1se=h, pls_r2=0.9,
                        gates_lam1=np.stack(gates1),
                        gates_lam0=np.stack(gates0))
    return d


# ------------------------------------------------- the partial correlation

def test_parcial_nan_quando_s_determina_g_e_r_perfeitamente():
    """If gate and reference are each strictly monotone in the prior, then
    rho_gs = rho_rs = 1, the denominator vanishes, and the partial correlation
    is UNDEFINED -- not zero. The function must say nan rather than divide by
    something near zero."""
    rng = np.random.default_rng(0)
    s = rng.random(400)
    g, r = 2.0 * s + 1.0, np.exp(s)
    assert mod.spearman(g, r) == pytest.approx(1.0, abs=1e-9)
    assert np.isnan(mod.spearman_parcial(g, r, s))


def test_parcial_proximo_de_zero_quando_s_quase_explica_tudo():
    """Not degenerate, but close: g and r are mostly the prior plus small
    independent noise. The raw Spearman is near 1 and the partial near 0."""
    rng = np.random.default_rng(42)
    s = rng.random(800)
    g = s + rng.normal(0, 0.02, 800)
    r = s + rng.normal(0, 0.02, 800)
    assert mod.spearman(g, r) > 0.95
    assert abs(mod.spearman_parcial(g, r, s)) < 0.25


def test_parcial_amplifica_ruido_quando_rho_gs_e_alto():
    """The denominator is sqrt((1-rho_gs^2)(1-rho_rs^2)), so at the measured
    rho(gate,prior) = 0.9655 the statistic multiplies the residual
    correlation by about 3.8. The script must report rho_gs so the reader can
    judge how much amplification each cell carries."""
    for rgs, esperado in ((0.9000, 2.29), (0.9655, 3.84), (0.9983, 17.16)):
        assert 1.0 / np.sqrt(1.0 - rgs ** 2) == pytest.approx(esperado,
                                                              abs=0.01)
    fonte = (RAIZ / "scripts" / "08_analise_condicional.py").read_text()
    assert "rho_gs" in fonte


def test_parcial_recupera_sinal_que_o_cru_esconde():
    """g and r share a component independent of s. The raw Spearman is
    dominated by s; the partial one must still see the shared component."""
    rng = np.random.default_rng(1)
    s = rng.random(600)
    extra = rng.normal(0, 1, 600)
    g = 10.0 * s + extra
    r = 10.0 * s + extra
    assert mod.spearman_parcial(g, r, s) > 0.5


def test_parcial_negativo_quando_o_residuo_e_anticorrelacionado():
    rng = np.random.default_rng(2)
    s = rng.random(600)
    extra = rng.normal(0, 1, 600)
    g, r = 10.0 * s + extra, 10.0 * s - extra
    assert mod.spearman_parcial(g, r, s) < -0.5


def test_parcial_igual_ao_cru_quando_s_e_independente():
    """With a prior unrelated to both, conditioning should change almost
    nothing."""
    rng = np.random.default_rng(3)
    g = rng.normal(0, 1, 800)
    r = g + rng.normal(0, 1, 800)
    s = rng.normal(0, 1, 800)
    assert mod.spearman_parcial(g, r, s) == pytest.approx(
        mod.spearman(g, r), abs=0.08)


def test_parcial_simetrica_em_g_e_r():
    rng = np.random.default_rng(4)
    s = rng.random(300)
    g, r = s + rng.normal(0, 0.5, 300), s + rng.normal(0, 0.5, 300)
    assert mod.spearman_parcial(g, r, s) == pytest.approx(
        mod.spearman_parcial(r, g, s))


def test_parcial_nan_sem_variacao():
    assert np.isnan(mod.spearman_parcial(np.ones(50), np.arange(50.0),
                                         np.arange(50.0)))


def test_parcial_nan_quando_s_determina_r_exatamente():
    """rho_rs = 1 makes the denominator vanish; nan is required, not a huge
    number from dividing by ~0."""
    rng = np.random.default_rng(5)
    s = rng.random(200)
    assert np.isnan(mod.spearman_parcial(rng.random(200), 3.0 * s + 1.0, s))


# -------------------------------------------------------------------- reading

def test_le_e_localiza_o_piso(tmp_path):
    pr = prior_degrau()
    rel = np.linspace(0, 1, P)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
         for s in range(NS)]
    c = mod.ler(escrever(tmp_path / "a", pr, g, g, rel))
    assert len(c["piso"]) == 223
    assert np.allclose(c["prior"][c["piso"]], 0.1)
    assert len(c["niveis"]) == 4


def test_lambda_ausente_e_erro_explicito(tmp_path):
    pr = prior_degrau()
    rel = np.linspace(0, 1, P)
    d = tmp_path / "a"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_relevance=rel,
                        pls_h_1se=70, pls_r2=0.9,
                        gates_lam0=np.stack([pr] * NS))
    with (d / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lam", "seed", "prior_arm",
                                          "agree_pls", "r2"])
        w.writeheader()
        w.writerow({"lam": 0.0, "seed": 0, "prior_arm": "literature",
                    "agree_pls": 0.1, "r2": 0.8})
    with pytest.raises(SystemExit, match="gates_lam1 not in"):
        mod.ler(d)


# -------------------------------------------------------------------- pairing

def _par_de_celulas(tmp_path, agree0_igual=True, h_ctl=70):
    pr = prior_degrau()
    rel = np.random.default_rng(9).random(P)
    g1 = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
          for s in range(NS)]
    g0 = [np.full(P, 0.5) + np.random.default_rng(100 + s).normal(0, 0.01, P)
          for s in range(NS)]
    a0 = [0.05 + 0.001 * s for s in range(NS)]
    lit = mod.ler(escrever(tmp_path / "lit", pr, g1, g0, rel, agree0=a0))
    b0 = a0 if agree0_igual else [x + 0.02 for x in a0]
    blk = mod.ler(escrever(tmp_path / "blk", pr, g1, g0, rel, arm="blocks",
                           agree0=b0, h=h_ctl))
    return lit, blk


def test_pareamento_aceita_lam0_identico(tmp_path):
    lit, blk = _par_de_celulas(tmp_path)
    mod.conferir(lit, blk)


def test_pareamento_recusa_lam0_diferente(tmp_path):
    lit, blk = _par_de_celulas(tmp_path, agree0_igual=False)
    with pytest.raises(SystemExit, match="agreement at lam=0 differs"):
        mod.conferir(lit, blk)


def test_pareamento_recusa_referencia_pls_diferente(tmp_path):
    lit, blk = _par_de_celulas(tmp_path, h_ctl=99)
    with pytest.raises(SystemExit, match="different PLS"):
        mod.conferir(lit, blk)


# ------------------------------------------------------------------ criteria

def test_contra_zero_suportada_quando_positiva():
    r = mod.contra_zero(np.full(NS, 0.3) + np.linspace(0, 0.01, NS))
    assert r["suportada"] and r["media"] > 0


def test_contra_zero_nao_suportada_quando_negativa():
    r = mod.contra_zero(np.full(NS, -0.3) + np.linspace(0, 0.01, NS))
    assert not r["suportada"]


def test_contra_zero_exige_significancia():
    rng = np.random.default_rng(11)
    r = mod.contra_zero(rng.normal(0.002, 0.5, NS))
    assert r["p"] >= mod.ALPHA and not r["suportada"]


def test_par_suportada_so_quando_a_supera_b():
    a = np.full(NS, 0.3) + np.linspace(0, 1e-3, NS)
    b = np.full(NS, 0.1) + np.linspace(0, 1e-3, NS)
    assert mod.par(a, b)["suportada"]
    assert not mod.par(b, a)["suportada"]


def test_par_indefinida_com_nan():
    a = np.full(NS, 0.3)
    b = a.copy()
    b[0] = np.nan
    assert mod.par(a, b)["indefinida"] is True


# ----------------------------------------------------------------- tie guard

def test_empatado_detecta_no_espectro_inteiro():
    assert mod.empatado([np.full(P, 0.5)])
    assert not mod.empatado([np.linspace(0, 1, P)])


def test_empatado_detecta_dentro_do_piso():
    g = np.linspace(0, 1, P)
    g[PISO] = 0.3
    assert mod.empatado([g], PISO)
    assert not mod.empatado([np.linspace(0, 1, P)], PISO)


# ----------------------------------------------------------------- constants

def test_constantes_vem_do_pre_registro():
    assert mod.LAM_FIXO == 1.0
    assert mod.ALPHA == 0.05
    assert mod.MIN_BANDAS_NIVEL == 10


def test_nao_afirma_dez_de_dez():
    """The raw metric favours blocks in 9 of the 10 partitions measured up to
    F003, not 10: literature wins partition 3. The wrong count was propagated
    into committed text once and must not come back."""
    for nome in ("08_analise_condicional.py", "07_raman_lambda1.py"):
        fonte = (RAIZ / "scripts" / nome).read_text()
        assert "10/10" not in fonte, nome
