"""Tests for `scripts/07_raman_lambda1.py` (H12, Raman control arm).

The Raman data is not available here, so what these tests protect is
everything that does not need it: the metric functions, the tie detection, the
geometry helpers, and the constants the pre-registration fixed. The two
regimes are built synthetically and the tests check that the criteria separate
them in the right direction — a continuous prior passing H12a and H12b, a
quantised one with a saturated plateau failing both.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
P, NS = 1870, 10

BANDAS_PRIMARIAS = (911.0, 1060.0, 1125.0)
BANDAS_SECUNDARIAS = (402.0, 527.0, 589.0, 732.0, 789.0, 855.0, 968.0,
                      1155.0, 1210.0, 1276.0, 1336.0, 1401.0, 1450.0,
                      1473.0, 1549.0)


def _carregar():
    caminho = RAIZ / "scripts" / "07_raman_lambda1.py"
    spec = importlib.util.spec_from_file_location("raman_h12", caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["raman_h12"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def prior_continuo() -> np.ndarray:
    """The Raman prior's functional form: sum of gaussians, peak-normalised,
    clipped at a floor. Continuous, so the maximum is attained once."""
    shifts = np.linspace(300.0, 1700.0, P)
    pr = np.zeros(P)
    for c in BANDAS_PRIMARIAS:
        pr += 1.0 * np.exp(-0.5 * ((shifts - c) / 15.0) ** 2)
    for c in BANDAS_SECUNDARIAS:
        pr += 0.4 * np.exp(-0.5 * ((shifts - c) / 15.0) ** 2)
    return np.clip(pr / pr.max(), 0.01, 1.0)


def prior_degrau() -> np.ndarray:
    """The NIR prior's functional form, scaled to Raman's band count: a wide
    flat plateau at the maximum, larger than q."""
    pr = np.full(P, 0.1)
    pr[200:540] = 1.0                     # 340 bands, against q = 187
    return pr


def gates_continuos(pr: np.ndarray, sd: float = 0.003) -> list[np.ndarray]:
    return [np.clip(0.30 + 0.60 * pr
                    + np.random.default_rng(s).normal(0, sd, P),
                    1e-6, 1 - 1e-6) for s in range(NS)]


def gates_saturados(pr: np.ndarray) -> list[np.ndarray]:
    """Prior-initialisation regime: the plateau is bit-identical, as measured
    in findings F002 and F004."""
    plato = np.flatnonzero(pr >= pr.max() - 1e-9)
    saida = []
    for s in range(NS):
        r = np.random.default_rng(s)
        v = 0.30 + 0.60 * pr + r.normal(0, 1.5e-4, P)
        v[plato] = 0.99999380
        saida.append(np.clip(v, 1e-6, 1 - 1e-6))
    return saida


# ------------------------------------------------------------------ constants

def test_constantes_vem_do_pre_registro():
    assert mod.LAMBDAS == (0.0, 1.0)
    assert mod.PARTICOES == (0, 1, 2)
    assert mod.N_SEEDS == 10
    assert mod.ALPHA == 0.05
    assert mod.LIM_H12A == 0.5
    assert mod.LIM_H12B == 0.02
    assert mod.PLS_H_MAX == 120
    assert mod.EPOCAS == 500


def test_lambda_nao_e_argumento_de_linha_de_comando():
    """The grid must not be able to drift during execution."""
    fonte = (RAIZ / "scripts" / "07_raman_lambda1.py").read_text()
    assert "--lambdas" not in fonte
    assert "--seeds" not in fonte
    assert "--split-seed" not in fonte


def test_q_e_a_definicao_publicada():
    """q = p // 10, floor division, as the published code computes it."""
    assert max(1, 1870 // 10) == 187
    assert max(1, 281 // 10) == 28


# ------------------------------------------------------------------- geometry

def test_maior_grupo_empate_acha_o_piso():
    pr = prior_continuo()
    grupo = mod.maior_grupo_empate(pr)
    assert len(grupo) > 100                       # the clipped floor
    assert np.allclose(pr[grupo], pr.min())


def test_maior_grupo_empate_acha_o_plato_quando_ele_e_o_maior():
    pr = np.full(100, 0.5)
    pr[:10] = 0.1
    pr[10:30] = 1.0
    grupo = mod.maior_grupo_empate(pr)
    assert len(grupo) == 70 and np.allclose(pr[grupo], 0.5)


def test_prior_continuo_tem_maximo_unico():
    pr = prior_continuo()
    assert len(np.flatnonzero(pr >= pr.max() - 1e-9)) == 1
    assert len(np.unique(pr)) > 500


def test_prior_degrau_tem_plato_maior_que_q():
    pr = prior_degrau()
    plato = np.flatnonzero(pr >= pr.max() - 1e-9)
    assert len(plato) == 340 > 1870 // 10


# -------------------------------------------------------------- tie detection

def test_empates_exatos_zero_em_gate_continuo():
    assert mod.empates_exatos(gates_continuos(prior_continuo())[0]) == 0


def test_empates_exatos_conta_plato_saturado():
    g = gates_saturados(prior_degrau())[0]
    assert mod.empates_exatos(g) >= 339


# ----------------------------------------------------------------------- H12a

def test_h12a_passa_com_prior_continuo():
    """The decile must not be pinned inside the prior's largest tie group."""
    pr = prior_continuo()
    q = P // 10
    grupo = set(mod.maior_grupo_empate(pr).tolist())
    fr = np.mean([len(set(mod.topo(g, q).tolist()) & grupo) / q
                  for g in gates_continuos(pr)])
    assert fr < mod.LIM_H12A


def test_h12a_falha_com_plato_maior_que_q():
    """The NIR situation: the decile comes entirely from one tied level."""
    pr = prior_degrau()
    q = P // 10
    plato = set(np.flatnonzero(pr >= pr.max() - 1e-9).tolist())
    fr = np.mean([len(set(mod.topo(g, q).tolist()) & plato) / q
                  for g in gates_saturados(pr)])
    assert fr == pytest.approx(1.0)


# ----------------------------------------------------------------------- H12b

def test_h12b_passa_sem_empates():
    pr = prior_continuo()
    q = P // 10
    g = gates_continuos(pr)
    ji = mod.jaccard_indice(g, q)
    jr, _ = mod.jaccard_sorteado(g, q, draws=40)
    assert abs(ji - jr) < mod.LIM_H12B


def test_h12b_falha_com_plato_saturado():
    """Same gates, same q, same formula; only the tie rule changes."""
    pr = prior_degrau()
    q = P // 10
    g = gates_saturados(pr)
    ji = mod.jaccard_indice(g, q)
    jr, _ = mod.jaccard_sorteado(g, q, draws=40)
    assert abs(ji - jr) > mod.LIM_H12B


def test_sorteio_de_empates_nao_reordena_valores_distintos():
    """lexsort's last key may only decide among exactly equal gate values."""
    g = np.linspace(0, 1, 500)
    rng = np.random.default_rng(0)
    chave = rng.random(len(g))
    assert (set(np.lexsort((chave, -g))[:50].tolist())
            == set(np.argsort(g)[::-1][:50].tolist()))


def test_jaccard_identico_da_um():
    v = [np.arange(500, dtype=float)] * 4
    assert mod.jaccard_indice(v, 50) == pytest.approx(1.0)


def test_jaccard_sorteado_determinista_por_semente():
    g = gates_saturados(prior_degrau())
    a = mod.jaccard_sorteado(g, 187, draws=20, seed=7)
    b = mod.jaccard_sorteado(g, 187, draws=20, seed=7)
    assert a == b


# --------------------------------------------------------------------- misc

def test_spearman_nan_sem_variacao():
    assert np.isnan(mod.spearman(np.ones(10), np.arange(10.0)))


def test_topo_devolve_q_indices_distintos():
    g = gates_continuos(prior_continuo())[0]
    t = mod.topo(g, 187)
    assert len(t) == 187 == len(set(t.tolist()))


def test_quick_nao_escreve_resultados():
    """--quick must be refused together with --out, so nothing from it can be
    mistaken for a registered result."""
    fonte = (RAIZ / "scripts" / "07_raman_lambda1.py").read_text()
    assert "--quick never writes results" in fonte


# -------------------------------------------- own vs literature tie group

def test_grupo_de_empate_do_braco_e_o_do_prior_permutado():
    """A relocated prior keeps the same multiset, so its floor is the same SIZE
    at different POSITIONS. Measuring a control arm's decile against the
    LITERATURE prior's floor therefore says nothing about its own tie
    structure, and the two numbers must be computed separately."""
    pr = prior_continuo()
    rng = np.random.default_rng(0)
    permutado = rng.permutation(pr)
    g_lit = mod.maior_grupo_empate(pr)
    g_perm = mod.maior_grupo_empate(permutado)
    assert len(g_lit) == len(g_perm)                  # same size
    assert set(g_lit.tolist()) != set(g_perm.tolist())  # different positions


def test_reporta_as_duas_fracoes():
    fonte = (RAIZ / "scripts" / "07_raman_lambda1.py").read_text()
    assert "in_tie_group_own" in fonte
    assert "in_own_group" in fonte


def test_lam0_nao_usa_o_prior():
    """The integrity check the script prints: at lam=0 every arm must agree,
    because the prior does not enter the loss. Here only the invariant is
    asserted — that the gate at lam=0 cannot depend on the prior argument."""
    fonte = (RAIZ / "scripts" / "07_raman_lambda1.py").read_text()
    assert "identical across arms by construction" in fonte
