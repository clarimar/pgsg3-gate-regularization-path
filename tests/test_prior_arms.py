"""Tests for the prior control arms (pre-registro H7-H9).

These run without torch: they check the permutation itself, which is what the
pre-registered criteria depend on.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]


def _permute_prior():
    """Extract the function without executing the script's module-level setup."""
    src = (RAIZ / "scripts/02_lambda_sweep_controlled.py").read_text()
    i = src.index("def permute_prior")
    j = src.index("# ------------------------------------------------------------------ data")
    ns = {"np": np}
    exec(src[i:j], ns)  # noqa: S102 - trecho proprio do repositorio
    return ns["permute_prior"]


permute_prior = _permute_prior()


def prior_realista():
    """Mesma forma do prior de literatura: fundo baixo e tres blocos elevados."""
    p = np.full(281, 0.1)
    p[20:27] = 0.6      # clorofila, 7 bandas
    p[100:134] = 1.0    # plato, 34 bandas
    p[180:197] = 0.8    # 1o sobretom, 17 bandas
    return p


def n_runs(mask) -> int:
    return int(np.sum(np.diff(np.r_[0, mask.astype(int), 0]) == 1))


# ------------------------------------------------------- invariantes
@pytest.mark.parametrize("modo", ["literature", "blocks", "shuffled"])
def test_multiset_de_valores_preservado(modo):
    """Todo braço deve ter exatamente os mesmos valores, só em outras posições.

    Sem isso o controle mudaria a FORÇA da ancoragem junto com a posição, e
    H7 não isolaria nada.
    """
    p = prior_realista()
    novo = permute_prior(p, modo, 42)
    np.testing.assert_allclose(np.sort(novo), np.sort(p))
    assert len(novo) == len(p)


def test_literature_nao_altera():
    p = prior_realista()
    np.testing.assert_array_equal(permute_prior(p, "literature", 42), p)


def test_literature_devolve_copia():
    """Não pode devolver o mesmo objeto: o chamador guarda os dois priors."""
    p = prior_realista()
    assert permute_prior(p, "literature", 0) is not p


# ----------------------------------------------------------- blocks
def test_blocks_preserva_numero_e_tamanho_dos_blocos():
    p = prior_realista()
    b = permute_prior(p, "blocks", 42)
    assert n_runs(b > 0.1) == n_runs(p > 0.1) == 3
    orig = sorted(np.diff(np.flatnonzero(np.diff(np.r_[0, (p > 0.1).astype(int), 0]))) [::2])
    novo = sorted(np.diff(np.flatnonzero(np.diff(np.r_[0, (b > 0.1).astype(int), 0]))) [::2])
    assert orig == novo


def test_blocks_move_os_blocos():
    p = prior_realista()
    assert not np.allclose(permute_prior(p, "blocks", 42), p)


def test_blocks_nao_sobrepoe():
    """Sobreposição mudaria o multiset; o teste acima já pegaria, mas aqui o
    motivo fica explícito para quem ler a falha."""
    p = prior_realista()
    for seed in range(25):
        b = permute_prior(p, "blocks", seed)
        assert int((b > 0.1).sum()) == int((p > 0.1).sum())


# --------------------------------------------------------- shuffled
def test_shuffled_fragmenta():
    p = prior_realista()
    s = permute_prior(p, "shuffled", 42)
    assert n_runs(s > 0.1) > 10, "permutacao completa deveria quebrar a contiguidade"


# ------------------------------------------------------ determinismo
@pytest.mark.parametrize("modo", ["blocks", "shuffled"])
def test_deterministico_por_semente(modo):
    """A permutação é por PARTIÇÃO: todas as sementes de modelo precisam ver o
    mesmo prior, senão o Jaccard de H9 cai por motivo trivial."""
    p = prior_realista()
    np.testing.assert_array_equal(permute_prior(p, modo, 7), permute_prior(p, modo, 7))
    assert not np.allclose(permute_prior(p, modo, 7), permute_prior(p, modo, 8))


def test_modo_invalido_rejeitado():
    with pytest.raises(ValueError, match="prior mode desconhecido"):
        permute_prior(prior_realista(), "aleatorio", 0)


# ------------------------------------------------- sanidade da premissa
@pytest.mark.parametrize("ocupacao", [0.2, 0.5, 0.8, 0.95])
def test_prior_denso_nunca_corrompe(ocupacao):
    """Com o eixo quase cheio, a realocação ou funciona preservando o multiset
    ou falha alto -- nunca sobrepõe blocos em silêncio, o que mudaria a força
    da ancoragem e invalidaria a comparação de H7.

    Um prior válido nunca tem sobreposição, logo o total elevado é sempre
    menor ou igual a p; o caso verdadeiramente impossível não é alcançável a
    partir de uma entrada válida. O que se testa aqui é a ausência de
    corrupção silenciosa, não a presença do erro.
    """
    p_len = 200
    k = int(ocupacao * p_len)
    denso = np.full(p_len, 0.1)
    denso[:k] = 1.0
    try:
        novo = permute_prior(denso, "blocks", 0)
    except SystemExit as e:
        assert "realocar" in str(e)
        return
    np.testing.assert_allclose(np.sort(novo), np.sort(denso))
