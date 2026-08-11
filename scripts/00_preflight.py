#!/usr/bin/env python
"""
Pré-voo do pgsg_3 (multi-alvo).

Responde a duas perguntas que travam o desenho do projeto:

  A) O dataset bioprocess_substrates carrega alvos além de glicose?
     -> Se sim, o braço Raman de pgsg_3 reaproveita G/T/P de pgsg_2 sem reescrita.

  B) Quais hiperparâmetros a PGSGv2Model de fato expõe?
     -> Define o espaço de busca real de pgsg_4 e checa se existe softmax/tau
        (o documento gating_4 assume tau de softmax, que é da PGSGModel superseded).

Uso:
    python inspect_pgsg3_preflight.py \
        --data-root ~/Dropbox/pgsg/pgsg_2 \
        --pgsg-v2   ~/Dropbox/pgsg/pgsg_1/pgsg_v2.py

Não escreve nada. Só lê e imprime.
"""

import argparse
import inspect
import os
import re
import sys
from pathlib import Path

SEP = "=" * 72


def head(title):
    print(f"\n{SEP}\n{title}\n{SEP}")


# ----------------------------------------------------------------------
# A) alvos disponíveis no bioprocess_substrates
# ----------------------------------------------------------------------

DATA_EXT = {".csv", ".tsv", ".npz", ".npy", ".h5", ".hdf5", ".parquet", ".mat", ".json"}
# nomes plausíveis de analito em bioprocessos
ANALYTE_HINT = re.compile(
    r"gluc|glc|lact|glut|gln|glu\b|ammon|nh4|acet|glyc|etoh|ethanol|"
    r"viable|vcd|density|titer|product|substrate|conc",
    re.I,
)


def find_data_files(root: Path, limit=200):
    hits = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in DATA_EXT:
            # ignora artefatos de saída
            if any(part in {"results", "figures", "paper", ".git"} for part in p.parts):
                continue
            hits.append(p)
            if len(hits) >= limit:
                break
    return sorted(hits, key=lambda p: -p.stat().st_size)


def describe(path: Path):
    ext = path.suffix.lower()
    size_mb = path.stat().st_size / 1e6
    print(f"\n--- {path}  ({size_mb:.1f} MB)")
    try:
        if ext in {".csv", ".tsv"}:
            import pandas as pd

            sep = "\t" if ext == ".tsv" else ","
            df = pd.read_csv(path, sep=sep, nrows=3)
            cols = list(df.columns)
            print(f"    colunas ({len(cols)}): {cols[:12]}{' ...' if len(cols) > 12 else ''}")
            cand = [c for c in cols if ANALYTE_HINT.search(str(c))]
            if cand:
                print(f"    >>> CANDIDATOS A ALVO: {cand}")
        elif ext in {".npz"}:
            import numpy as np

            with np.load(path, allow_pickle=True) as z:
                print(f"    chaves: {list(z.files)}")
                for k in z.files:
                    try:
                        print(f"      {k}: shape={z[k].shape} dtype={z[k].dtype}")
                    except Exception:
                        pass
                cand = [k for k in z.files if ANALYTE_HINT.search(k)]
                if cand:
                    print(f"    >>> CANDIDATOS A ALVO: {cand}")
        elif ext in {".h5", ".hdf5"}:
            import h5py

            with h5py.File(path, "r") as f:
                keys = []
                f.visit(keys.append)
                print(f"    datasets: {keys[:20]}{' ...' if len(keys) > 20 else ''}")
                cand = [k for k in keys if ANALYTE_HINT.search(k)]
                if cand:
                    print(f"    >>> CANDIDATOS A ALVO: {cand}")
        elif ext == ".parquet":
            import pandas as pd

            df = pd.read_parquet(path)
            print(f"    colunas: {list(df.columns)[:20]}")
        elif ext == ".json":
            import json

            with open(path) as f:
                obj = json.load(f)
            if isinstance(obj, dict):
                print(f"    chaves: {list(obj)[:20]}")
    except Exception as e:
        print(f"    [não lido: {type(e).__name__}: {e}]")


def check_dataset(data_root: Path):
    head("A) bioprocess_substrates — alvos disponíveis")
    if not data_root.exists():
        print(f"!! caminho inexistente: {data_root}")
        return
    files = find_data_files(data_root)
    if not files:
        print("!! nenhum arquivo de dados encontrado sob", data_root)
        return
    print(f"{len(files)} arquivo(s) de dados. Os 10 maiores:")
    for p in files[:10]:
        describe(p)

    # tenta também o pacote ramanbench, se instalado
    try:
        import ramanbench  # noqa: F401

        print("\n[ramanbench instalado — inspecionando API]")
        import ramanbench as rb

        print("    atributos:", [a for a in dir(rb) if not a.startswith("_")][:25])
    except ImportError:
        print("\n[ramanbench não instalado neste ambiente — ok, checagem por arquivo acima]")


# ----------------------------------------------------------------------
# B) hiperparâmetros reais da PGSGv2Model
# ----------------------------------------------------------------------

def check_model(pgsg_v2_path: Path):
    head("B) PGSGv2Model — hiperparâmetros expostos")
    if not pgsg_v2_path.exists():
        print(f"!! caminho inexistente: {pgsg_v2_path}")
        return

    src = pgsg_v2_path.read_text(errors="replace")

    # b1) softmax existe neste arquivo?
    print("\n[b1] busca por softmax / temperatura")
    for pat, label in [
        (r"softmax", "softmax"),
        (r"\btau\b|\btemperature\b", "tau/temperature"),
        (r"sigmoid", "sigmoid"),
    ]:
        n = len(re.findall(pat, src, re.I))
        print(f"    {label:20s}: {n} ocorrência(s)")
    print("    -> se softmax=0 e sigmoid>0, o 'tau' do documento gating_4 NÃO existe aqui.")

    # b2) assinatura do __init__ e do treino
    print("\n[b2] assinaturas")
    sys.path.insert(0, str(pgsg_v2_path.parent))
    try:
        mod = __import__(pgsg_v2_path.stem)
    except Exception as e:
        print(f"    [import falhou: {type(e).__name__}: {e}]")
        print("    fallback: definições encontradas por regex ->")
        for m in re.finditer(r"^\s*def (__init__|fit|train)\s*\(([^)]*)\)", src, re.M):
            print(f"      def {m.group(1)}({' '.join(m.group(2).split())})")
        return

    for name, obj in vars(mod).items():
        if not inspect.isclass(obj) or name.startswith("_"):
            continue
        print(f"\n    class {name}")
        for meth in ("__init__", "fit", "forward"):
            fn = getattr(obj, meth, None)
            if fn is None:
                continue
            try:
                sig = inspect.signature(fn)
            except (TypeError, ValueError):
                continue
            print(f"      {meth}{sig}")
            for pname, p in sig.parameters.items():
                if p.default is not inspect.Parameter.empty:
                    print(f"        {pname:22s} default = {p.default!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="~/Dropbox/pgsg/pgsg_2")
    ap.add_argument("--pgsg-v2", default="~/Dropbox/pgsg/pgsg_1/pgsg_v2.py")
    a = ap.parse_args()

    check_dataset(Path(os.path.expanduser(a.data_root)))
    check_model(Path(os.path.expanduser(a.pgsg_v2)))

    head("Decisões que a saída acima destrava")
    print("  1. Há analitos além de glicose?  SIM -> braço Raman em pgsg_3.")
    print("                                   NÃO -> Corn sozinho sustenta pgsg_3.")
    print("  2. Existe softmax/tau na PGSGv2? NÃO (esperado) -> reescrever o espaço")
    print("     de busca de pgsg_4 sobre os hiperparâmetros reais (lambda, hidden,")
    print("     lr, weight_decay, epochs).")


if __name__ == "__main__":
    main()
