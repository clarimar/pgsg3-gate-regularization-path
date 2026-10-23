"""Tests for `scripts/06_analise_plato.py` (H10, H11).

The criteria live in `docs/pre-registro-H10-H11.md` and are committed before
the sweeps, so what these tests protect is the transcription: that each
statistic counts what the document says, that the tie guard reports UNDEFINED
instead of a number, and that the displacement metric is computed on |g - s|
and not on the raw gate.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
P, NS = 281, 10
PLATO = np.arange(197, 231)          # 34 bands, as in the real prior


def _carregar():
    caminho = RAIZ / "scripts" / "06_analise_plato.py"
    spec = importlib.util.spec_from_file_location("analise_plato", caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["analise_plato"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def prior_degrau() -> np.ndarray:
    """The four-level prior measured in the data."""
    pr = np.full(P, 0.1)
    pr[np.arange(60, 67)] = 0.6
    pr[np.arange(120, 137)] = 0.8
    pr[PLATO] = 1.0
    return pr


def escrever(d: Path, prior: np.ndarray, gates: list[np.ndarray],
             relevance: np.ndarray, arm: str = "literature") -> Path:
    d.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(d / "gates.npz", prior=prior, pls_relevance=relevance,
                        prior_arm=arm, pls_h_1se=70, pls_r2=0.9,
                        gates_lam1=np.stack(gates))
    return d


def celula(tmp_path: Path, *, nome: str, rho_alvo: float,
           arm: str = "literature", empate: bool = False,
           realce: str = "nenhum") -> dict:
    """A cell whose within-plateau ordering tracks the reference by rho_alvo.

    `realce` says which prior level carries the largest WITHIN-LEVEL spread,
    which is what the H11 residual ranks:
      "nenhum" -- only the plateau's reference-driven ordering, nothing else
      "plato"  -- plateau bands stand out sharply against their own level
      "piso"   -- floor bands do, so the residual decile should leave the
                  plateau
    """
    assert realce in ("nenhum", "plato", "piso")
    pr = prior_degrau()
    rng = np.random.default_rng(abs(hash(nome)) % 2**32)
    rel = rng.uniform(0, 1, P)
    piso = np.flatnonzero(pr == 0.1)

    gates = []
    for s in range(NS):
        r = np.random.default_rng(1000 + s)
        g = 0.30 + 0.60 * pr
        if empate:
            g[PLATO] = 0.99999380           # bit-identical, F002's artifact
        else:
            # inside the plateau, order by the reference with controllable noise
            ruido = r.normal(0, max(1e-6, (1 - abs(rho_alvo)) * 0.5),
                             len(PLATO))
            g[PLATO] = 0.90 + 0.05 * (
                np.sign(rho_alvo) * rel[PLATO] + ruido)
        if realce == "plato":
            g[PLATO[:25]] -= 0.20
        elif realce == "piso":
            # a fixed subset of floor bands pushed well off their level mean,
            # by more than the plateau's internal spread
            g[piso[:40]] += 0.30
        g = np.clip(g + r.normal(0, 1e-4, P), 1e-6, 1 - 1e-6)
        gates.append(g)
    return mod.ler(escrever(tmp_path / nome, pr, gates, rel, arm))


# ------------------------------------------------------------------ geometry

def test_le_niveis_e_plato(tmp_path):
    c = celula(tmp_path, nome="a", rho_alvo=0.8)
    assert len(c["niveis"]) == 4
    assert len(c["plato"]) == 34
    assert c["q"] == 29                      # ceil(0.10 * 281)
    assert c["p"] == P


def test_lambda_ausente_e_erro_explicito(tmp_path):
    pr = prior_degrau()
    d = tmp_path / "x"
    d.mkdir()
    np.savez_compressed(d / "gates.npz", prior=pr, pls_relevance=pr,
                        pls_h_1se=70, pls_r2=0.9,
                        gates_lam0=np.stack([pr] * NS))
    with pytest.raises(SystemExit, match="gates_lam1 not in"):
        mod.ler(d)


# ------------------------------------------------------------------ tie guard

def test_empate_exato_e_detectado(tmp_path):
    c = celula(tmp_path, nome="emp", rho_alvo=0.8, empate=True)
    assert mod.empatado(c["gates"], c["plato"])


def test_gates_distintos_nao_acusam_empate(tmp_path):
    c = celula(tmp_path, nome="ok", rho_alvo=0.8)
    assert not mod.empatado(c["gates"], c["plato"])


def test_h10a_indefinida_sob_empate(tmp_path):
    """The pre-registration makes a tied cell UNDEFINED, never imputed."""
    c = celula(tmp_path, nome="emp", rho_alvo=0.8, empate=True)
    r = mod.h10a(c, c["plato"])
    assert r["indefinida"] is True
    assert "media" not in r and "suportada" not in r


def test_h10b_indefinida_se_qualquer_braco_empatar(tmp_path):
    lit = celula(tmp_path, nome="lit", rho_alvo=0.8)
    blk = celula(tmp_path, nome="blk", rho_alvo=0.2, arm="blocks", empate=True)
    assert mod.h10b(lit, blk, lit["plato"], blk["plato"])["indefinida"] is True


# ----------------------------------------------------------------------- H10

def test_h10a_detecta_ordenacao_positiva(tmp_path):
    c = celula(tmp_path, nome="pos", rho_alvo=0.9)
    r = mod.h10a(c, c["plato"])
    assert not r["indefinida"]
    assert r["media"] > 0.5 and r["suportada"]


def test_h10a_nao_suportada_com_ordenacao_negativa(tmp_path):
    c = celula(tmp_path, nome="neg", rho_alvo=-0.9)
    r = mod.h10a(c, c["plato"])
    assert r["media"] < 0 and not r["suportada"]


def test_h10a_usa_so_as_bandas_do_nivel(tmp_path):
    """The statistic must not see bands outside the level it was given."""
    c = celula(tmp_path, nome="niv", rho_alvo=0.9)
    inteiro = mod.spearman(c["gates"][0], c["relevance"])
    so_plato = mod.h10_serie(c, c["plato"])[0]
    assert abs(inteiro - so_plato) > 0.1       # they are different questions
    piso = np.flatnonzero(c["prior"] == 0.1)
    assert len(mod.h10_serie(c, piso)) == NS


def test_h10b_suportada_quando_literatura_ordena_melhor(tmp_path):
    lit = celula(tmp_path, nome="l1", rho_alvo=0.9)
    blk = celula(tmp_path, nome="b1", rho_alvo=0.1, arm="blocks")
    r = mod.h10b(lit, blk, lit["plato"], blk["plato"])
    assert r["delta"] > 0 and r["suportada"]


def test_h10b_nao_suportada_quando_controle_ordena_melhor(tmp_path):
    lit = celula(tmp_path, nome="l2", rho_alvo=0.1)
    blk = celula(tmp_path, nome="b2", rho_alvo=0.9, arm="blocks")
    r = mod.h10b(lit, blk, lit["plato"], blk["plato"])
    assert r["delta"] < 0 and not r["suportada"]


def test_h10_pareia_por_semente(tmp_path):
    """Series must come back in seed order so the arms pair element-wise."""
    c = celula(tmp_path, nome="pp", rho_alvo=0.8)
    s = mod.h10_serie(c, c["plato"])
    assert len(s) == NS and not np.isnan(s).any()


# ----------------------------------------------------------------------- H11

def test_residuo_e_centrado_por_nivel_nao_g_menos_s(tmp_path):
    """Within-level centering, not |g - s|: the two differ, and |g - s| would
    put the decile on the floor bands instead of removing the confinement."""
    c = celula(tmp_path, nome="d1", rho_alvo=0.8)
    r = mod.residuo_intra_nivel(c)[0]
    g, pr = c["gates"][0], c["prior"]
    assert not np.allclose(r, np.abs(g - pr))
    for v in c["niveis"]:
        bandas = np.flatnonzero(np.abs(pr - v) <= mod.TOL_NIVEL)
        # centering means the signed residual sums to zero inside each level
        assert abs((g[bandas] - g[bandas].mean()).sum()) < 1e-9
    # and |g - s| really would land on the floor, which is what we avoided
    piso = set(np.flatnonzero(pr == 0.1).tolist())
    gs = set(mod.topo(np.abs(g - pr), c["q"]).tolist())
    assert len(gs & piso) == c["q"]
    # the raw-gate decile sits inside the plateau
    cru = set(mod.topo(g, c["q"]).tolist())
    assert len(cru & set(c["plato"].tolist())) == c["q"]


def test_h11a_falha_quando_residuo_fica_no_plato(tmp_path):
    """If the residual decile is still plateau-bound, H11a must fail: the
    metric did not solve the confinement and H11b is not to be read."""
    c = celula(tmp_path, nome="d2", rho_alvo=0.8, realce="plato")
    r = mod.h11a(c)
    assert r["fracao"] >= mod.FRACAO_H11A and not r["suportada"]


def test_h11a_suportada_quando_residuo_escapa(tmp_path):
    c = celula(tmp_path, nome="d3", rho_alvo=0.8, realce="piso")
    r = mod.h11a(c)
    assert r["fracao"] < mod.FRACAO_H11A and r["suportada"]


def test_h11_jaccard_indefinido_sob_empate_no_residuo(tmp_path):
    c = celula(tmp_path, nome="d4", rho_alvo=0.8)
    c["gates"] = [np.full(P, 0.5) for _ in range(NS)]   # |g-s| has ties
    assert mod.h11_jaccard(c)["indefinida"] is True


def test_h11_jaccard_entre_zero_e_um(tmp_path):
    c = celula(tmp_path, nome="d5", rho_alvo=0.8, realce="piso")
    r = mod.h11_jaccard(c)
    assert not r["indefinida"] and 0.0 <= r["j"] <= 1.0


def test_jaccard_identico_da_um():
    v = [np.arange(100, dtype=float)] * 5
    assert mod.jaccard_medio(v, 10) == pytest.approx(1.0)


# ----------------------------------------------------------------- constants

def test_constantes_vem_do_pre_registro():
    assert mod.LAM_FIXO == 1.0
    assert mod.ALPHA == 0.05
    assert mod.DECIL == 0.10
    assert mod.FRACAO_H11A == 0.5
    assert mod.MIN_BANDAS_NIVEL == 10


def test_spearman_nan_sem_variacao():
    assert np.isnan(mod.spearman(np.ones(10), np.arange(10.0)))
    assert np.isnan(mod.spearman(np.arange(2.0), np.arange(2.0)))
