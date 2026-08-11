"""Smoke test: garante que o modelo vendorizado é o correto."""
import hashlib
from pathlib import Path

MODEL = Path(__file__).resolve().parents[1] / "src/pgsg_3/m_model/pgsg_v2.py"


def test_modelo_existe():
    assert MODEL.exists(), "PGSGv2Model ausente — ver PROVENANCE.md"


def test_modelo_nao_usa_softmax():
    """A PGSGv2 usa sigmoide independente por banda.
    Softmax indicaria contaminação pela PGSGModel superseded."""
    src = MODEL.read_text(errors="replace").lower()
    assert "sigmoid" in src
    assert "softmax" not in src, "softmax encontrado: modelo possivelmente errado"


def test_hash_registrado():
    prov = MODEL.parent / "PROVENANCE.md"
    registrado = [l for l in prov.read_text().splitlines() if "SHA-256" in l]
    assert registrado, "hash não registrado"
    atual = hashlib.sha256(MODEL.read_bytes()).hexdigest()
    assert atual in registrado[0], f"hash divergente: {atual}"
