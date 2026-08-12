"""Testes da PGSGv3Model.

O teste central é `test_lambda_zero_reproduz_v2`: ele garante que a
subclasse não introduziu desvio algum no caminho λ=0. Como o laço de
treino da v3 é uma cópia do da v2 (o arquivo vendorizado não pode ser
modificado, sob pena de invalidar o hash de proveniência), esse teste é
a única proteção contra divergência silenciosa entre os dois.
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from pgsg_3.m_model.pgsg_v3 import (  # noqa: E402
    PGSGv3Model,
    kl_bernoulli,
    kl_bernoulli_np,
)
from pgsg_3.m_model.pgsg_v2 import PGSGv2Model  # noqa: E402

try:
    from pgsg_1.ingestion import SpectralDataset
except ImportError:  # pragma: no cover
    pytest.skip("pacote pgsg_1 indisponível", allow_module_level=True)


P = 40
N = 120
META = {
    "domain": "synthetic",
    "source": "test",
    "target_name": "y",
    "target_unit": "au",
    "wavelength_unit": "nm",
}


def dados_sinteticos(seed=0):
    """Espectros sintéticos onde só uma região carrega sinal."""
    rng = np.random.default_rng(seed)
    wl = np.linspace(900.0, 1300.0, P)
    X = rng.normal(0, 1, size=(N, P))
    informativas = (wl >= 950) & (wl <= 1050)
    y = X[:, informativas].sum(axis=1) + rng.normal(0, 0.1, size=N)
    return SpectralDataset(X=X, y=y, wavelengths=wl, metadata=dict(META))


def prior_sintetico():
    wl = np.linspace(900.0, 1300.0, P)
    s = np.full(P, 0.1)
    s[(wl >= 950) & (wl <= 1050)] = 1.0
    return s / s.max()


# ------------------------------------------------------------------ KL
def test_kl_nula_quando_igual():
    g = np.array([0.1, 0.5, 0.9])
    assert kl_bernoulli_np(g, g) == pytest.approx(0.0, abs=1e-12)


def test_kl_positiva_quando_diferente():
    assert kl_bernoulli_np(np.array([0.9, 0.9]), np.array([0.1, 0.1])) > 0


def test_kl_torch_bate_com_numpy():
    g = np.array([0.2, 0.6, 0.95])
    s = np.array([0.5, 0.5, 0.10])
    a = float(kl_bernoulli(torch.tensor(g), torch.tensor(s)))
    assert a == pytest.approx(kl_bernoulli_np(g, s), rel=1e-9)


def test_kl_e_media_nao_soma():
    """Média sobre bandas: λ comparável entre p diferentes."""
    g = np.full(10, 0.9); s = np.full(10, 0.1)
    g2 = np.full(1000, 0.9); s2 = np.full(1000, 0.1)
    assert kl_bernoulli_np(g, s) == pytest.approx(kl_bernoulli_np(g2, s2), rel=1e-9)


# --------------------------------------------------- equivalência λ=0
def test_lambda_zero_reproduz_v2():
    """λ=0 deve reproduzir a PGSGv2Model exatamente.

    Se este teste falhar, o laço copiado divergiu do original — corrigir
    antes de qualquer execução de experimento.
    """
    ds = dados_sinteticos()
    prior = prior_sintetico()

    v2 = PGSGv2Model(hidden=8, max_epochs=15, patience=5, seed=7)
    v2.fit(ds, prior=prior)

    v3 = PGSGv3Model(lam=0.0, hidden=8, max_epochs=15, patience=5, seed=7)
    v3.fit(ds, prior=prior)

    np.testing.assert_allclose(v3.gates, v2.gates, rtol=0, atol=0)
    np.testing.assert_allclose(v3.predict(ds), v2.predict(ds), rtol=0, atol=0)
    assert v3.train_history["best_epoch"] == v2.train_history["best_epoch"]


def test_lambda_zero_sem_prior_reproduz_v2():
    """A condição não-informada também deve ser idêntica."""
    ds = dados_sinteticos()
    v2 = PGSGv2Model(hidden=8, max_epochs=15, patience=5, seed=3)
    v2.fit(ds, prior=None)
    v3 = PGSGv3Model(lam=0.0, hidden=8, max_epochs=15, patience=5, seed=3)
    v3.fit(ds, prior=None)
    np.testing.assert_allclose(v3.gates, v2.gates, rtol=0, atol=0)


# ------------------------------------------------------- comportamento
def test_lambda_alto_aproxima_gate_do_prior():
    """λ grande deve puxar o gate para o prior."""
    ds = dados_sinteticos()
    prior = prior_sintetico()

    baixo = PGSGv3Model(lam=0.0, hidden=8, max_epochs=40, patience=40, seed=1)
    baixo.fit(ds, prior=prior)
    alto = PGSGv3Model(lam=100.0, hidden=8, max_epochs=40, patience=40, seed=1)
    alto.fit(ds, prior=prior)

    assert alto.kl_final < baixo.kl_final, (
        f"KL com lam=100 ({alto.kl_final:.3e}) deveria ser menor que "
        f"com lam=0 ({baixo.kl_final:.3e})"
    )


def test_lam_positivo_sem_prior_falha():
    ds = dados_sinteticos()
    m = PGSGv3Model(lam=0.1, hidden=8, max_epochs=5, seed=0)
    with pytest.raises(ValueError, match="exige um prior"):
        m.fit(ds, prior=None)


def test_lam_negativo_rejeitado():
    with pytest.raises(ValueError, match="lam deve ser"):
        PGSGv3Model(lam=-1.0)


def test_historico_registra_kl_e_lam():
    ds = dados_sinteticos()
    m = PGSGv3Model(lam=0.01, hidden=8, max_epochs=10, patience=10, seed=0)
    m.fit(ds, prior=prior_sintetico())
    h = m.train_history
    assert h["lam"] == 0.01
    assert len(h["kl_history"]) == len(h["val_losses"])
    assert m.kl_final is not None
