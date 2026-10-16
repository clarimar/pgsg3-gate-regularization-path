"""Tests for the vendorized grouped split and calibrated PLS reference.

These run without torch, so they verify the protocol machinery independently
of the model.
"""

import numpy as np
import pytest

from pgsg_3.g_ingest.grouped import (
    group_folds,
    group_split,
    pls_reference_relevance,
    select_h,
)


def groups_sinteticos(n_groups=100, per_group=2):
    return np.repeat(np.arange(n_groups), per_group)


# --------------------------------------------------------------- split
def test_split_nao_quebra_grupo():
    """The defining property: no fruit may appear on both sides."""
    g = groups_sinteticos()
    tr, te = group_split(g, 0.2, seed=0)
    assert not (set(g[tr]) & set(g[te])), "a group landed on both sides"


def test_split_cobre_tudo_sem_sobrepor():
    g = groups_sinteticos()
    tr, te = group_split(g, 0.2, seed=0)
    assert len(tr) + len(te) == len(g)
    assert not (set(tr.tolist()) & set(te.tolist()))


def test_split_fracao_aproximada():
    g = groups_sinteticos(n_groups=100)
    _, te = group_split(g, 0.2, seed=0)
    assert 0.15 <= len(te) / len(g) <= 0.25


def test_split_deterministico_por_semente():
    g = groups_sinteticos()
    a1, b1 = group_split(g, 0.2, seed=7)
    a2, b2 = group_split(g, 0.2, seed=7)
    np.testing.assert_array_equal(a1, a2)
    np.testing.assert_array_equal(b1, b2)
    _, b3 = group_split(g, 0.2, seed=8)
    assert not np.array_equal(b1, b3)


def test_split_grupos_desiguais():
    """723 fruits measured twice plus 2 singletons: sizes are not uniform."""
    g = np.concatenate([np.repeat(np.arange(723), 2), [723, 724]])
    tr, te = group_split(g, 0.2, seed=0)
    assert not (set(g[tr]) & set(g[te]))
    assert len(tr) + len(te) == len(g) == 1448


# --------------------------------------------------------------- folds
def test_folds_nao_quebram_grupo():
    g = groups_sinteticos()
    for tr, va in group_folds(g, 5, seed=0):
        assert not (set(g[tr]) & set(g[va]))


def test_folds_particionam():
    g = groups_sinteticos()
    folds = group_folds(g, 5, seed=0)
    assert len(folds) == 5
    vistos = np.concatenate([va for _, va in folds])
    np.testing.assert_array_equal(np.sort(vistos), np.arange(len(g)))


# ------------------------------------------------------------ select_h
def test_select_h_regra_1se_e_mais_parcimoniosa():
    hs = np.arange(1, 11)
    mean = np.array([10, 6, 3, 2.1, 2.0, 2.05, 2.1, 2.2, 2.4, 3.0])
    se = np.full(10, 0.2)
    h_cvmin, h_1se = select_h(hs, mean, se)
    assert h_cvmin == 5
    assert h_1se <= h_cvmin
    assert mean[h_1se - 1] <= mean[h_cvmin - 1] + se[h_cvmin - 1]


# ------------------------------------------------- referencia de relevancia
def test_referencia_pls_aponta_para_bandas_informativas():
    """Only a known window carries signal; |coef| must be largest there."""
    rng = np.random.default_rng(0)
    n, p = 300, 60
    X = rng.normal(size=(n, p))
    informativas = slice(20, 30)
    y = X[:, informativas].sum(axis=1) + rng.normal(0, 0.05, n)

    ref = pls_reference_relevance(X, y, None, h_max=20, n_folds=5, seed=0)
    rel = ref["relevance"]
    assert rel.shape == (p,)
    assert rel[informativas].mean() > 5 * np.delete(rel, np.r_[20:30]).mean()
    assert 1 <= ref["h_1se"] <= ref["h_cvmin"] <= ref["h_max_effective"]


def test_referencia_pls_usa_folds_agrupados_quando_pedido():
    rng = np.random.default_rng(1)
    n_g, per = 80, 2
    g = np.repeat(np.arange(n_g), per)
    X = rng.normal(size=(n_g * per, 30))
    y = X[:, 5:10].sum(axis=1) + rng.normal(0, 0.1, n_g * per)
    ref = pls_reference_relevance(X, y, g, h_max=12, n_folds=4, seed=0)
    assert ref["relevance"].shape == (30,)
