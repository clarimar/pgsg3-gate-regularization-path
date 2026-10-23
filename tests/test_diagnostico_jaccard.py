"""Tests for `scripts/05_diagnostico_jaccard.py`.

The script is descriptive, which is exactly why it needs tests: a wrong number
here would be read as an explanation of a verdict rather than as a claim that
could be checked. The identity it rests on is churn == q <=> J == 1.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
P, NS = 281, 10


def _carregar():
    caminho = RAIZ / "scripts" / "05_diagnostico_jaccard.py"
    spec = importlib.util.spec_from_file_location("diag_jaccard", caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["diag_jaccard"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def escrever(d: Path, prior: np.ndarray, gates1: list[np.ndarray],
             gates0: list[np.ndarray] | None = None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    extra = {} if gates0 is None else {"gates_lam0": np.stack(gates0)}
    np.savez_compressed(d / "gates.npz", prior=prior,
                        pls_relevance=np.linspace(0, 1, len(prior)),
                        pls_h_1se=70, pls_r2=0.9,
                        gates_lam1=np.stack(gates1), **extra)
    return d


def prior_com_plato(n_plato: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pr = rng.uniform(0.0, 0.4, P)
    pr[np.arange(40, 40 + n_plato)] = 1.0
    return pr


# ------------------------------------------------------------------ geometry

def test_q_e_o_teto_do_decil():
    """q = ceil(0.10 * 281) = 29, not 28. The arithmetic of plateau against
    decile depends on this, so it is pinned."""
    assert int(np.ceil(0.10 * 281)) == 29


def test_plato_conta_bandas_empatadas_no_maximo(tmp_path):
    pr = prior_com_plato(34)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 1e-4, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["plato"] == 34
    assert r["q"] == 29
    assert r["p"] == P


def test_plato_nao_confunde_valor_alto_com_maximo(tmp_path):
    """A band just below the maximum is not on the plateau."""
    pr = prior_com_plato(10)
    pr[200] = 1.0 - 1e-6
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 1e-4, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["plato"] == 10


# ------------------------------------------------------- churn / J identity

def test_churn_igual_q_implica_jaccard_um(tmp_path):
    """Identical deciles across seeds: J must be exactly 1 and churn == q."""
    pr = prior_com_plato(34)
    base = np.zeros(P)
    base[np.arange(40, 69)] = 1.0            # exactly 29 clear winners
    g = [base + np.random.default_rng(s).normal(0, 1e-6, P) * 0.0
         + np.random.default_rng(s).uniform(0, 1e-9, P) for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["churn"] == r["q"]
    assert r["jaccard"] == pytest.approx(1.0)
    assert r["nucleo"] == r["q"]


def test_churn_maior_que_q_implica_jaccard_menor_que_um(tmp_path):
    pr = prior_com_plato(34)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.05, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["churn"] > r["q"]
    assert r["jaccard"] < 1.0


def test_jaccard_reproduz_o_do_script_de_varredura(tmp_path):
    """05 must compute the same Jaccard that 02 wrote into aggregate.csv, or
    the diagnostic would be explaining a different number than the verdict."""
    import itertools
    pr = prior_com_plato(34)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.03, P)
         for s in range(NS)]
    q = int(np.ceil(0.10 * P))
    tops = [set(np.argsort(x)[::-1][:q].tolist()) for x in g]
    esperado = float(np.mean([len(a & b) / len(a | b)
                              for a, b in itertools.combinations(tops, 2)]))
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["jaccard"] == pytest.approx(esperado)


# ------------------------------------------------------------ tie detection

def test_detecta_empate_exato_entre_gates_treinados(tmp_path):
    """If trained gates were tied at the maximum, argsort would order by band
    index and the Jaccard would be partly an artifact. The script has to say
    so, so it must detect the condition."""
    pr = prior_com_plato(34)
    g = [np.ones(P) for _ in range(NS)]      # degenerate: everything tied
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["gate_max_ties"] > 1


def test_gates_continuos_nao_acusam_empate(tmp_path):
    pr = prior_com_plato(34)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["gate_max_ties"] == 1


# ------------------------------------------------------- tie-breaking source

def test_rho_dados_positivo_quando_sinal_decide(tmp_path):
    """Plateau ties broken by a consistent data preference."""
    pr = prior_com_plato(34)
    sinal = np.zeros(P)
    sinal[np.arange(40, 74)] = np.linspace(0.3, 0.0, 34)
    g1 = [pr * 0.5 + sinal + np.random.default_rng(s).normal(0, 0.004, P)
          for s in range(NS)]
    g0 = [0.2 + sinal * 2 + np.random.default_rng(s).normal(0, 0.01, P)
          for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g1, g0), 1.0, 0.10)
    assert r["corr_dados"] > 0.3


def test_rho_dados_nulo_quando_ruido_decide(tmp_path):
    pr = prior_com_plato(34)
    g1 = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.05, P)
          for s in range(NS)]
    g0 = [0.2 + np.random.default_rng(1000 + s).normal(0, 0.01, P)
          for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g1, g0), 1.0, 0.10)
    assert abs(r["corr_dados"]) < 0.35


def test_rho_dados_nan_sem_variacao(tmp_path):
    """Every plateau band wins every time: nothing to correlate, and the
    script must return nan rather than a spurious number."""
    pr = prior_com_plato(20)
    base = np.zeros(P)
    base[np.arange(40, 60)] = 1.0
    g1 = [base + np.random.default_rng(s).uniform(0, 1e-9, P)
          for s in range(NS)]
    g0 = [0.2 + np.random.default_rng(s).normal(0, 0.01, P) for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g1, g0), 1.0, 0.10)
    assert np.isnan(r["corr_dados"])


# ------------------------------------------------------- prior is quantized

def test_conta_niveis_distintos_do_prior(tmp_path):
    """The observed priors report ties == p, which only happens if every value
    is shared. The number of distinct levels is what makes that legible."""
    rng = np.random.default_rng(0)
    niveis = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    pr = niveis[rng.integers(0, 5, P)]
    pr[np.arange(40, 74)] = 1.0
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["niveis"] == 6
    assert r["empatados"] == P          # every band's value is shared


def test_prior_continuo_nao_acusa_empate_total(tmp_path):
    pr = np.linspace(0.01, 1.0, P)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["niveis"] == P
    assert r["empatados"] == 0


# ------------------------------------------------- always / sometimes split

def test_particiona_plato_em_sempre_e_as_vezes(tmp_path):
    pr = prior_com_plato(34)
    base = np.zeros(P)
    base[np.arange(40, 74)] = 1.0
    base[np.arange(40, 46)] -= 0.1       # six bands that will lose slots
    g = [base + np.random.default_rng(s).normal(0, 1e-4, P) for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert r["n_sempre"] + r["n_as_vezes"] == r["plato"]
    assert r["n_sempre"] == 28 and r["n_as_vezes"] == 6


def test_forca_g0_separa_os_dois_grupos(tmp_path):
    """Ties broken against the data: the losing bands must be the ones the
    data-only gate had pushed above 0.5."""
    pr = prior_com_plato(34)
    plato = np.arange(40, 74)
    preferidas = plato[:8]
    g0b = np.full(P, 0.5)
    g0b[preferidas] += 0.06
    g1b = 0.30 + 0.60 * pr
    g1b[preferidas] -= 0.05
    g0 = [g0b + np.random.default_rng(s).normal(0, 0.004, P)
          for s in range(NS)]
    g1 = [g1b + np.random.default_rng(s).normal(0, 0.003, P)
          for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g1, g0), 1.0, 0.10)
    assert r["corr_dados"] < -0.3
    assert r["forca_as_vezes"] > r["forca_sempre"]
    assert r["p_mw"] < 0.05


def test_mannwhitney_nan_quando_um_grupo_e_vazio(tmp_path):
    """Plateau smaller than q: nobody loses a slot, so there is no comparison
    to make and the script must not invent one."""
    pr = prior_com_plato(20)
    base = np.zeros(P)
    base[np.arange(40, 60)] = 1.0
    g1 = [base + np.random.default_rng(s).uniform(0, 1e-9, P)
          for s in range(NS)]
    g0 = [np.full(P, 0.5) + np.random.default_rng(s).normal(0, 0.01, P)
          for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g1, g0), 1.0, 0.10)
    assert r["n_as_vezes"] == 0
    assert np.isnan(r["p_mw"])


# ------------------------------------------------- external reference check

def _regime_observado(rel_favorece_perdedoras: bool):
    """The regime seen in the data: 4-level prior, plateau 34 > q 29, plateau
    ties broken against the lam=0 gate. The external reference either
    corroborates that or contradicts it."""
    rng = np.random.default_rng(0)
    niveis = np.array([0.0, 1 / 3, 2 / 3, 1.0])
    pr = niveis[rng.integers(0, 3, P)]
    plato = np.arange(40, 74)
    pr[plato] = 1.0
    perdedoras = plato[:8]

    rel = rng.uniform(0, 0.1, P)
    rel[perdedoras if rel_favorece_perdedoras else plato[8:]] += 0.5

    g0b = np.full(P, 0.5)
    g0b[perdedoras] += 0.06
    g0, g1 = [], []
    for s in range(NS):
        r = np.random.default_rng(500 + s)
        g0.append(g0b + r.normal(0, 0.004, P))
        v = 0.30 + 0.60 * pr
        v[perdedoras] -= 0.05
        g1.append(np.clip(v + r.normal(0, 0.003, P), 1e-6, 1 - 1e-6))
    return pr, rel, g1, g0


def test_rho_pls_concorda_com_rho_dados(tmp_path):
    pr, rel, g1, g0 = _regime_observado(True)
    d = tmp_path / "a"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_relevance=rel,
                        pls_h_1se=70, pls_r2=0.9,
                        gates_lam1=np.stack(g1), gates_lam0=np.stack(g0))
    r = mod.diagnosticar(d, 1.0, 0.10)
    assert r["corr_dados"] < -0.3 and r["corr_pls"] < -0.3
    assert r["rel_as_vezes"] > r["rel_sempre"]
    assert r["p_mw_pls"] < 0.05


def test_rho_pls_pode_discordar_de_rho_dados(tmp_path):
    """The case that must not be hidden: the gate's own lam=0 output says one
    thing and the external reference says the opposite. The effect is then a
    property of the model, not of the bands."""
    pr, rel, g1, g0 = _regime_observado(False)
    d = tmp_path / "a"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_relevance=rel,
                        pls_h_1se=70, pls_r2=0.9,
                        gates_lam1=np.stack(g1), gates_lam0=np.stack(g0))
    r = mod.diagnosticar(d, 1.0, 0.10)
    assert r["corr_dados"] < -0.3
    assert r["corr_pls"] > 0.3
    assert r["rel_sempre"] > r["rel_as_vezes"]


def test_rho_pls_independe_do_gate_lam0(tmp_path):
    """rho pls must be computable with no lam=0 block at all; that is the
    point of having it."""
    pr, rel, g1, _ = _regime_observado(True)
    d = tmp_path / "a"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_relevance=rel,
                        pls_h_1se=70, pls_r2=0.9, gates_lam1=np.stack(g1))
    r = mod.diagnosticar(d, 1.0, 0.10)
    assert np.isnan(r["corr_dados"])
    assert r["corr_pls"] < -0.3


def test_sem_referencia_pls_degrada_para_nan(tmp_path):
    pr = prior_com_plato(34)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
         for s in range(NS)]
    d = tmp_path / "a"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_h_1se=70, pls_r2=0.9,
                        gates_lam1=np.stack(g))
    r = mod.diagnosticar(d, 1.0, 0.10)
    assert np.isnan(r["corr_pls"]) and np.isnan(r["p_mw_pls"])


def test_niveis_valores_lista_valor_e_contagem(tmp_path):
    pr, rel, g1, g0 = _regime_observado(True)
    d = tmp_path / "a"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_relevance=rel,
                        pls_h_1se=70, pls_r2=0.9,
                        gates_lam1=np.stack(g1), gates_lam0=np.stack(g0))
    r = mod.diagnosticar(d, 1.0, 0.10)
    assert len(r["niveis_valores"]) == r["niveis"] == 4
    assert sum(c for _, c in r["niveis_valores"]) == P
    assert r["niveis_valores"][-1] == (1.0, 34)   # the plateau is the top level


# ---------------------------------------------------------------- robustness

def test_lambda_ausente_e_erro_explicito(tmp_path):
    pr = prior_com_plato(34)
    g = [pr * 0.5 for _ in range(NS)]
    d = escrever(tmp_path / "a", pr, g)
    with pytest.raises(SystemExit, match="gates_lam0.5 not in"):
        mod.diagnosticar(d, 0.5, 0.10)


def test_funciona_sem_gates_lam0(tmp_path):
    """The literature runs predate some npz keys; a missing lam=0 block must
    degrade to nan, not crash."""
    pr = prior_com_plato(34)
    g = [pr * 0.5 + np.random.default_rng(s).normal(0, 0.01, P)
         for s in range(NS)]
    r = mod.diagnosticar(escrever(tmp_path / "a", pr, g), 1.0, 0.10)
    assert np.isnan(r["corr_dados"])
