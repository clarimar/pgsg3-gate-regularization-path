"""Smoke test: garante que o modelo vendorizado é o correto."""
import ast
import hashlib
from pathlib import Path

MODEL = Path(__file__).resolve().parents[1] / "src/pgsg_3/m_model/pgsg_v2.py"


def _identificadores(src: str) -> set[str]:
    """Nomes e atributos usados no CÓDIGO.

    Comentários não existem na AST e docstrings são nós Constant, que não
    inspecionamos — logo, menções em prosa não contaminam a checagem. Foi
    exatamente o falso positivo da primeira versão deste teste: o próprio
    pgsg_v2.py comenta que usa sigmoide *em vez* de softmax global.
    """
    nomes = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name):
            nomes.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            nomes.add(node.attr.lower())
        elif isinstance(node, ast.arg):
            nomes.add(node.arg.lower())
    return nomes


def test_modelo_existe():
    assert MODEL.exists(), "PGSGv2Model ausente — ver PROVENANCE.md"


def test_gate_e_sigmoide_nao_softmax():
    """A PGSGv2 usa sigmoide independente por banda.

    Softmax no código (não em comentário) indicaria contaminação pela
    PGSGModel superseded, cujo gradiente colapsa em p alto.
    """
    ids = _identificadores(MODEL.read_text(errors="replace"))
    assert any("sigmoid" in i for i in ids), "sigmoide não encontrada no código"
    achados = sorted(i for i in ids if "softmax" in i)
    assert not achados, f"softmax no código: {achados} — modelo possivelmente errado"


def test_sem_tau_de_softmax():
    """Registra que não há temperatura de softmax exposta.

    Se este teste passar a falhar, o espaço de busca do pgsg_3 (ADR-0001,
    decisão 3) precisa ser revisto: significaria que um τ existe de fato.
    """
    ids = _identificadores(MODEL.read_text(errors="replace"))
    suspeitos = sorted(i for i in ids if i in {"tau", "temperature", "temp"})
    assert not suspeitos, f"hiperparâmetro de temperatura encontrado: {suspeitos}"


def test_hash_registrado():
    prov = MODEL.parent / "PROVENANCE.md"
    registrado = [l for l in prov.read_text().splitlines() if "SHA-256" in l]
    assert registrado, "hash não registrado"
    atual = hashlib.sha256(MODEL.read_bytes()).hexdigest()
    assert atual in registrado[0], f"hash divergente: {atual}"
