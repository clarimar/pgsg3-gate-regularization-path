#!/usr/bin/env python
"""
Reconciliação da ablação de prior no ramo NIR (Mango DMC v3, temporada 4).

MOTIVO
------
pgsg_1 e pgsg_2 relatam resultados incompatíveis para a mesma comparação,
no mesmo dataset, com a mesma arquitetura:

    condição        pgsg_1 (5 sementes)   pgsg_2 (10 sementes)
    PGSGv2-lit      0.806                 0.7933 ± 0.0080
    PGSGv2-rand     0.76                  0.7983 ± 0.0077
    Δ_prior         +0.048                -0.005

A discrepância concentra-se na condição NÃO INFORMADA (~5 SD); a condição
lit difere apenas 0.013. Ambos os manuscritos estão em revisão e o pgsg_2
cita o pgsg_1.

O QUE ESTE SCRIPT FAZ
---------------------
Roda as duas condições no MESMO processo, com o MESMO split e as MESMAS
sementes, e reporta:

  (1) média ± SD sobre 10 sementes      -> comparável a pgsg_2
  (2) média ± SD sobre as sementes 0-4  -> comparável a pgsg_1
  (3) diferença pareada por semente + teste de Wilcoxon

Isso separa três hipóteses:
  H_sementes  — o número de sementes explica a diferença
                => (1) e (2) divergem entre si
  H_condição  — 'rand' significava coisas diferentes nos dois estudos
                => ambas reproduzem pgsg_2 e nenhuma reproduz pgsg_1
  H_protocolo — split ou pré-processamento diferiam
                => nenhuma das duas reproduz nenhum dos publicados

NÃO escreve nada fora de --out. Não altera o modelo vendorizado.

USO
---
    # 1) descobrir os pontos de entrada do repo pgsg_1
    python reconcile_prior_ablation.py --pgsg1-root ~/Dropbox/pgsg/pgsg_1 --dry-run

    # 2) rodar, apontando o loader identificado no passo 1
    python reconcile_prior_ablation.py \
        --pgsg1-root ~/Dropbox/pgsg/pgsg_1 \
        --loader carregar_mango_s4 \
        --out results/reconcile_prior_ablation.csv
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import os
import sys
from pathlib import Path

import numpy as np

# valores publicados, para a tabela de reconciliação
PUB = {
    "pgsg_1": {"lit": 0.806, "rand": 0.76, "n_seeds": 5},
    "pgsg_2": {"lit": 0.7933, "lit_sd": 0.0080, "rand": 0.7983, "rand_sd": 0.0077, "n_seeds": 10},
}

SEP = "=" * 74


def head(t):
    print(f"\n{SEP}\n{t}\n{SEP}")


# ---------------------------------------------------------------- import
def carregar_modulo(path: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"não foi possível carregar {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def listar_entradas(mod, rotulo):
    """Imprime callables plausíveis para loader e prior."""
    print(f"\n[{rotulo}] callables públicos:")
    for nome, obj in sorted(vars(mod).items()):
        if nome.startswith("_") or not callable(obj):
            continue
        try:
            sig = str(inspect.signature(obj))
        except (TypeError, ValueError):
            sig = "(...)"
        marca = ""
        low = nome.lower()
        if any(k in low for k in ("load", "carreg", "prepar", "dataset", "mango", "read")):
            marca = "   <-- candidato a LOADER"
        elif "prior" in low:
            marca = "   <-- candidato a PRIOR"
        print(f"    {nome}{sig}{marca}")


# ------------------------------------------------------------------ dados
def split_estratificado(y: np.ndarray, frac_teste=0.2, seed=42, n_estratos=5):
    """Split estratificado por quantis de y — protocolo dos dois papers."""
    rng = np.random.default_rng(seed)
    quantis = np.quantile(y, np.linspace(0, 1, n_estratos + 1)[1:-1])
    estrato = np.digitize(y, quantis)
    idx_teste = []
    for e in np.unique(estrato):
        idx = np.flatnonzero(estrato == e)
        rng.shuffle(idx)
        k = int(round(frac_teste * len(idx)))
        idx_teste.append(idx[:k])
    idx_teste = np.sort(np.concatenate(idx_teste))
    mascara = np.ones(len(y), dtype=bool)
    mascara[idx_teste] = False
    return np.flatnonzero(mascara), idx_teste


def normalizar_saida(obj):
    """Aceita SpectralDataset, dict ou tupla; devolve (X, y, wl)."""
    if hasattr(obj, "X") and hasattr(obj, "y"):
        return np.asarray(obj.X), np.asarray(obj.y), np.asarray(getattr(obj, "wavelengths", []))
    if isinstance(obj, dict):
        return np.asarray(obj["X"]), np.asarray(obj["y"]), np.asarray(obj.get("wavelengths", []))
    if isinstance(obj, (tuple, list)) and len(obj) >= 2:
        X, y = np.asarray(obj[0]), np.asarray(obj[1])
        wl = np.asarray(obj[2]) if len(obj) > 2 else np.arange(X.shape[1])
        return X, y, wl
    raise TypeError(f"saída do loader não reconhecida: {type(obj)}")


# ------------------------------------------------------------------ rodada
def r2(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true).ravel(), np.asarray(y_pred).ravel()
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def treinar(ModelCls, DatasetCls, Xtr, ytr, wl, Xte, yte, prior, seed):
    modelo = ModelCls(seed=seed)
    train = DatasetCls(X=Xtr, y=ytr, wavelengths=wl)
    test = DatasetCls(X=Xte, y=yte, wavelengths=wl)
    modelo.fit(train, prior=prior)
    pred = modelo.predict(test) if hasattr(modelo, "predict") else modelo.transform(test)
    return r2(yte, pred)


def resumo(vals):
    v = np.asarray(vals, dtype=float)
    return v.mean(), v.std(ddof=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg1-root", default="~/Dropbox/pgsg/pgsg_1")
    ap.add_argument("--model-file", default=None,
                    help="default: <pgsg3>/src/pgsg_3/m_model/pgsg_v2.py (a cópia vendorizada)")
    ap.add_argument("--loader", default=None, help="nome da função de carga em run_experiment_v2.py")
    ap.add_argument("--prior-fn", default="make_literature_prior")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--split-seed", type=int, default=42)
    ap.add_argument("--out", default="results/reconcile_prior_ablation.csv")
    ap.add_argument("--dry-run", action="store_true", help="só lista pontos de entrada e sai")
    a = ap.parse_args()

    root = Path(os.path.expanduser(a.pgsg1_root))
    model_file = Path(os.path.expanduser(a.model_file)) if a.model_file else \
        Path(__file__).resolve().parents[1] / "src/pgsg_3/m_model/pgsg_v2.py"

    head("Módulos")
    print(f"modelo   : {model_file}")
    mod_model = carregar_modulo(model_file, "pgsg_v2_reconc")
    runner_path = root / "run_experiment_v2.py"
    mod_run = None
    if runner_path.exists():
        print(f"runner   : {runner_path}")
        sys.path.insert(0, str(root))
        try:
            mod_run = carregar_modulo(runner_path, "run_experiment_v2_reconc")
        except Exception as e:
            print(f"  [import do runner falhou: {type(e).__name__}: {e}]")
    else:
        print(f"!! runner não encontrado em {runner_path}")

    if a.dry_run or a.loader is None:
        listar_entradas(mod_model, "pgsg_v2.py")
        if mod_run is not None:
            listar_entradas(mod_run, "run_experiment_v2.py")
        print("\nEscolha o loader e rode de novo com --loader <nome>.")
        return

    # ------------------------------------------------------------ carga
    fonte = mod_run if (mod_run and hasattr(mod_run, a.loader)) else mod_model
    loader = getattr(fonte, a.loader)
    X, y, wl = normalizar_saida(loader())
    print(f"\ndados: X={X.shape}  y={y.shape}  p={X.shape[1]}")

    prior_fn = getattr(mod_run, a.prior_fn, None) or getattr(mod_model, a.prior_fn, None)
    if prior_fn is None:
        raise SystemExit(f"função de prior '{a.prior_fn}' não encontrada")
    try:
        prior = np.asarray(prior_fn(wl))
    except TypeError:
        prior = np.asarray(prior_fn())
    print(f"prior: shape={prior.shape}  min={prior.min():.3f}  max={prior.max():.3f}")

    ModelCls = getattr(mod_model, "PGSGv2Model")
    DatasetCls = getattr(mod_model, "SpectralDataset")

    idx_tr, idx_te = split_estratificado(y, 0.2, a.split_seed)
    print(f"split: treino={len(idx_tr)}  teste={len(idx_te)}  (seed={a.split_seed})")
    Xtr, ytr, Xte, yte = X[idx_tr], y[idx_tr], X[idx_te], y[idx_te]

    # ----------------------------------------------------------- rodada
    head(f"Rodando 2 condições x {a.seeds} sementes")
    linhas = []
    for seed in range(a.seeds):
        for cond, p in (("lit", prior), ("rand", None)):
            score = treinar(ModelCls, DatasetCls, Xtr, ytr, wl, Xte, yte, p, seed)
            linhas.append({"seed": seed, "condicao": cond, "r2": score})
            print(f"  seed={seed:2d}  {cond:5s}  R2={score:.4f}")

    # ------------------------------------------------------------ saída
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["seed", "condicao", "r2"])
        w.writeheader()
        w.writerows(linhas)
    print(f"\nescrito: {out}")

    # --------------------------------------------------- reconciliação
    def por_cond(cond, ate=None):
        v = [r["r2"] for r in linhas if r["condicao"] == cond and (ate is None or r["seed"] < ate)]
        return resumo(v)

    head("Reconciliação")
    lit10, litsd10 = por_cond("lit")
    rnd10, rndsd10 = por_cond("rand")
    lit5, litsd5 = por_cond("lit", 5)
    rnd5, rndsd5 = por_cond("rand", 5)

    print(f"{'':22s} {'lit':>18s} {'rand':>18s} {'Δ_prior':>10s}")
    print(f"{'pgsg_1 publicado':22s} {PUB['pgsg_1']['lit']:>18.4f} "
          f"{PUB['pgsg_1']['rand']:>18.4f} {PUB['pgsg_1']['lit']-PUB['pgsg_1']['rand']:>+10.4f}")
    print(f"{'pgsg_2 publicado':22s} "
          f"{PUB['pgsg_2']['lit']:>10.4f}±{PUB['pgsg_2']['lit_sd']:.4f} "
          f"{PUB['pgsg_2']['rand']:>10.4f}±{PUB['pgsg_2']['rand_sd']:.4f} "
          f"{PUB['pgsg_2']['lit']-PUB['pgsg_2']['rand']:>+10.4f}")
    print(f"{'este, sementes 0-4':22s} {lit5:>10.4f}±{litsd5:.4f} "
          f"{rnd5:>10.4f}±{rndsd5:.4f} {lit5-rnd5:>+10.4f}")
    print(f"{'este, sementes 0-9':22s} {lit10:>10.4f}±{litsd10:.4f} "
          f"{rnd10:>10.4f}±{rndsd10:.4f} {lit10-rnd10:>+10.4f}")

    # teste pareado por semente
    pares = {}
    for r in linhas:
        pares.setdefault(r["seed"], {})[r["condicao"]] = r["r2"]
    dif = np.array([pares[s]["lit"] - pares[s]["rand"] for s in sorted(pares)])
    print(f"\ndiferença pareada por semente: média={dif.mean():+.4f}  SD={dif.std(ddof=1):.4f}")
    try:
        from scipy.stats import wilcoxon
        stat, pval = wilcoxon(dif)
        print(f"Wilcoxon pareado: W={stat:.1f}  p={pval:.4f}")
    except Exception as e:
        print(f"[Wilcoxon indisponível: {e}]")

    head("Leitura do resultado")
    print("  sementes 0-4 ≈ pgsg_1 e 0-9 ≈ pgsg_2  -> o número de sementes explica")
    print("  ambas ≈ pgsg_2, nenhuma ≈ pgsg_1      -> 'rand' diferia; revisar pgsg_1")
    print("  nenhuma bate com nenhum publicado     -> split ou pré-processamento diferiam")
    print("\nAtenção: 'rand' aqui é prior=None (θ₀=0, portas em 0.5), conforme")
    print("pgsg_1 §4.3 e pgsg_2 §6.3. Se o pgsg_1 tiver usado θ₀ aleatório de fato,")
    print("essa é a origem da divergência e o script não a reproduz sozinho.")


if __name__ == "__main__":
    main()
