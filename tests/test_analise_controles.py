"""Tests for `scripts/04_analise_controles.py` (H7/H8/H9).

An analysis script that fails silently is worse than one that crashes: it
prints a verdict either way. These tests build minimal sweep directories with
known answers and check that each pre-registered criterion counts what the
pre-registration says it counts, that the two on-disk schemas are both read
(the literature runs predate the `prior_arm` column), and that the pairing
guard refuses to produce verdicts for mismatched partitions.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
LAMS = [0.0, 1.0, 10.0]
SEEDS = list(range(10))


def _carregar():
    """The module name starts with a digit, so import it by path."""
    caminho = RAIZ / "scripts" / "04_analise_controles.py"
    spec = importlib.util.spec_from_file_location("analise_controles", caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["analise_controles"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


# ------------------------------------------------------------------ fixtures

def escrever_dir(d: Path, *, arm: str, agree: dict[float, np.ndarray],
                 jaccard: dict[float, float], prior: np.ndarray,
                 relevance: np.ndarray, h: int = 70, r2: float = 0.9,
                 schema_antigo: bool = False) -> Path:
    """A sweep directory with exactly the fields the analysis reads."""
    d.mkdir(parents=True, exist_ok=True)
    campos = ["lam", "seed", "init"] + ([] if schema_antigo else ["prior_arm"]) \
        + ["agree_pls", "r2"]
    linhas = []
    for lam in agree:
        for i, s in enumerate(SEEDS):
            r = {"lam": lam, "seed": s, "init": "zero",
                 "agree_pls": float(agree[lam][i]), "r2": r2}
            if not schema_antigo:
                r["prior_arm"] = arm
            linhas.append(r)
    with (d / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)

    with (d / "aggregate.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lam", "prior_arm", "jaccard"])
        w.writeheader()
        for lam in agree:
            w.writerow({"lam": lam, "prior_arm": arm,
                        "jaccard": jaccard.get(lam, 0.6)})

    np.savez_compressed(d / "gates.npz", prior=prior, pls_relevance=relevance,
                        pls_h_1se=h, pls_r2=r2,
                        lambdas=np.asarray(list(agree)),
                        seeds=np.asarray(SEEDS))
    return d


def serie_const(v: float, jitter: float = 0.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return v + (rng.normal(0, jitter, len(SEEDS)) if jitter else
                np.zeros(len(SEEDS)))


def par(tmp_path: Path, *, lit1: float, ctl1: float, a0: float = 0.05,
        jlit: float = 0.95, jctl: float = 0.95, arm: str = "blocks",
        jitter: float = 0.01, nome: str = "p") -> tuple[dict, dict]:
    """A literature/control pair on the same partition: lam=0 shared exactly,
    as it must be when the prior does not enter the loss."""
    base = serie_const(a0, jitter, seed=1)
    prior = np.linspace(0, 1, 40)
    rel = np.linspace(0, 1, 40)
    lit = escrever_dir(
        tmp_path / f"{nome}_lit",
        arm="literature",
        agree={0.0: base, 1.0: serie_const(lit1, jitter, 2),
               10.0: serie_const(lit1 - 0.01, jitter, 3)},
        jaccard={1.0: jlit}, prior=prior, relevance=rel, schema_antigo=True)
    ctl = escrever_dir(
        tmp_path / f"{nome}_{arm}",
        arm=arm,
        agree={0.0: base, 1.0: serie_const(ctl1, jitter, 4),
               10.0: serie_const(ctl1 - 0.01, jitter, 5)},
        jaccard={1.0: jctl}, prior=prior, relevance=rel)
    return mod.ler_arm(lit), mod.ler_arm(ctl)


# -------------------------------------------------------------------- reading

def test_le_schema_antigo_sem_prior_arm(tmp_path):
    """The literature runs were produced before --prior existed."""
    lit, _ = par(tmp_path, lit1=0.27, ctl1=0.27)
    assert lit["arm"] == "literature"
    assert "prior_arm" not in (lit["dir"] / "runs.csv").read_text().split("\n")[0]


def test_le_schema_novo_com_prior_arm(tmp_path):
    _, ctl = par(tmp_path, lit1=0.27, ctl1=0.46, arm="blocks")
    assert ctl["arm"] == "blocks"


def test_serie_ordenada_por_semente(tmp_path):
    """Pairing is element-wise, so the order must be the seed order and not
    the order the rows happen to sit in the file."""
    lit, _ = par(tmp_path, lit1=0.27, ctl1=0.27)
    assert mod.seeds(lit, 1.0) == SEEDS
    assert len(mod.serie(lit, 1.0)) == len(SEEDS)


def test_lambda_ausente_e_erro_explicito(tmp_path):
    lit, _ = par(tmp_path, lit1=0.27, ctl1=0.27)
    with pytest.raises(SystemExit, match="no runs at lam=0.5"):
        mod.serie(lit, 0.5)


# -------------------------------------------------------------------- pairing

def test_pareamento_aceita_particao_igual(tmp_path):
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.46)
    mod.conferir_pareamento(lit, ctl)   # must not raise


def test_pareamento_recusa_lam0_diferente(tmp_path):
    """lam=0 never uses the prior, so a difference there means the arms are
    not the same partition. The script must withhold verdicts, not average
    over the mistake."""
    lit, _ = par(tmp_path, lit1=0.27, ctl1=0.46, nome="a")
    _, ctl = par(tmp_path, lit1=0.27, ctl1=0.46, a0=0.09, nome="b")
    with pytest.raises(SystemExit, match="agreement at lam=0 differs"):
        mod.conferir_pareamento(lit, ctl)


def test_pareamento_recusa_referencia_pls_diferente(tmp_path):
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.46)
    z = dict(np.load(ctl["dir"] / "gates.npz"))
    z["pls_h_1se"] = np.asarray(99)
    np.savez_compressed(ctl["dir"] / "gates.npz", **z)
    with pytest.raises(SystemExit, match="different PLS"):
        mod.conferir_pareamento(lit, mod.ler_arm(ctl["dir"]))


def test_pareamento_recusa_sementes_diferentes(tmp_path):
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.46)
    linhas = [r for r in csv.DictReader((ctl["dir"] / "runs.csv").open())
              if int(r["seed"]) != 9]
    with (ctl["dir"] / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    with pytest.raises(SystemExit, match="same model seeds"):
        mod.conferir_pareamento(lit, mod.ler_arm(ctl["dir"]))


# ------------------------------------------------------------------------- H7

def test_h7_suportada_quando_literatura_vence(tmp_path):
    lit, ctl = par(tmp_path, lit1=0.28, ctl1=0.12)
    r = mod.h7_particao(lit, ctl, mod.LAM_FIXO)
    assert r["suportada"] and r["delta"] > 0


def test_h7_nao_suportada_quando_controle_vence(tmp_path):
    """The case the control exists to detect."""
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.46)
    r = mod.h7_particao(lit, ctl, mod.LAM_FIXO)
    assert not r["suportada"] and r["delta"] < 0


def test_h7_nao_suportada_quando_empatam(tmp_path):
    """'Equals or exceeds' refutes: a tie is not support for H7."""
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.27, jitter=0.0)
    r = mod.h7_particao(lit, ctl, mod.LAM_FIXO)
    assert not r["suportada"]


def test_h7_exige_significancia_nao_so_sinal(tmp_path):
    """A positive mean with a large spread must not pass on sign alone."""
    lit, ctl = par(tmp_path, lit1=0.2705, ctl1=0.27, jitter=0.12)
    r = mod.h7_particao(lit, ctl, mod.LAM_FIXO)
    assert r["p"] >= mod.ALPHA and not r["suportada"]


def test_h7_usa_o_lambda_fixado_nao_o_argmax(tmp_path):
    """The primary comparison is at lam=1, fixed before the data. Here the
    control's argmax is at lam=10, and that must not be what H7 reads."""
    base = serie_const(0.05, 0.01, 1)
    prior = np.linspace(0, 1, 40)
    lit = mod.ler_arm(escrever_dir(
        tmp_path / "lit", arm="literature", schema_antigo=True,
        agree={0.0: base, 1.0: serie_const(0.30, 0.01, 2),
               10.0: serie_const(0.10, 0.01, 3)},
        jaccard={1.0: 0.95}, prior=prior, relevance=prior))
    ctl = mod.ler_arm(escrever_dir(
        tmp_path / "ctl", arm="blocks",
        agree={0.0: base, 1.0: serie_const(0.10, 0.01, 4),
               10.0: serie_const(0.90, 0.01, 5)},
        jaccard={1.0: 0.95}, prior=prior, relevance=prior))
    assert mod.argmax_lam(ctl) == 10.0
    assert mod.h7_particao(lit, ctl, mod.LAM_FIXO)["suportada"]


# ------------------------------------------------------------------------- H8

def test_h8_suportada_quando_ancoragem_nao_eleva(tmp_path):
    _, ctl = par(tmp_path, lit1=0.27, ctl1=0.05, a0=0.05, jitter=0.01)
    assert mod.h8_particao(ctl)["suportada"]


def test_h8_nao_suportada_quando_ancoragem_eleva(tmp_path):
    _, ctl = par(tmp_path, lit1=0.27, ctl1=0.46, a0=0.05)
    r = mod.h8_particao(ctl)
    assert not r["suportada"] and r["delta"] > 0


def test_h8_suportada_quando_ancoragem_piora(tmp_path):
    """Negative also supports H8: the criterion is 'not significantly
    positive', not 'no effect'."""
    _, ctl = par(tmp_path, lit1=0.27, ctl1=0.01, a0=0.20)
    r = mod.h8_particao(ctl)
    assert r["suportada"] and r["delta"] < 0


# ------------------------------------------------------------------------- H9

@pytest.mark.parametrize("jlit,jctl,esperado", [
    (0.95, 0.9500, True),    # identical
    (0.95, 0.9100, True),    # |diff| = 0.040 -> inside
    (0.95, 0.9049, True),    # |diff| = 0.0451 -> inside, near the edge
    (0.95, 0.8999, False),   # |diff| = 0.0501 -> outside, near the edge
    (0.95, 0.8900, False),   # |diff| = 0.060 -> outside
    (0.95, 0.9900, True),    # control ABOVE literature still counts
    (0.60, 0.9500, False),   # control stable where literature is not
])
def test_h9_limiar(tmp_path, jlit, jctl, esperado):
    """Expected values written out, not recomputed from the implementation."""
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.27, jlit=jlit, jctl=jctl)
    assert mod.h9_particao(lit, ctl)["suportada"] is esperado


def test_h9_sinaliza_proximidade_do_limiar(tmp_path):
    """A difference landing on 0.05 is decided by float noise
    (0.95 - 0.90 = 0.04999999999999998, which passes a strict '< 0.05').
    The criterion is the pre-registration's and is not changed here, but the
    report must flag a verdict taken at the resolution of its own threshold."""
    lit, ctl = par(tmp_path, lit1=0.27, ctl1=0.27, jlit=0.95, jctl=0.90)
    r = mod.h9_particao(lit, ctl)
    assert r["limite"], "a diff of 0.050 must be marked as borderline"
    longe = mod.h9_particao(*par(tmp_path, lit1=0.27, ctl1=0.27,
                                 jlit=0.95, jctl=0.93, nome="longe"))
    assert not longe["limite"]


def test_h9_simetrica(tmp_path):
    """|diff| < tol, so which arm is higher must not change the verdict."""
    a, b = par(tmp_path, lit1=0.27, ctl1=0.27, jlit=0.95, jctl=0.92, nome="a")
    c, d = par(tmp_path, lit1=0.27, ctl1=0.27, jlit=0.92, jctl=0.95, nome="b")
    assert mod.h9_particao(a, b)["suportada"] == mod.h9_particao(c, d)["suportada"]


# --------------------------------------------------------------- constants

def test_constantes_vem_do_pre_registro():
    """These three numbers are the pre-registration's, not tuning knobs."""
    assert mod.LAM_FIXO == 1.0
    assert mod.ALPHA == 0.05
    assert mod.TOL_JACCARD == 0.05


def test_wilcoxon_nao_quebra_com_diferencas_nulas(tmp_path):
    """scipy raises on an all-zero difference vector; the criterion needs a
    p-value of 1, not a traceback."""
    assert mod.par_wilcoxon(np.zeros(10)) == 1.0
