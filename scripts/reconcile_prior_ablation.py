#!/usr/bin/env python
"""
Reconciliação da ablação de prior no ramo NIR — v3.

Corrige a v2: Preprocessor.transform devolve (X, y), não um SpectralDataset,
e Preprocessor.fit aceita safety_datasets — o mecanismo pelo qual pgsg_1
remove as bandas com variância nula em QUALQUER das cinco temporadas
(protocolo "união das bandas zeradas", Opção C), chegando a p=281.

Sem safety_datasets o p sai diferente de 281 e a comparação com os valores
publicados não vale.

CONTEXTO
--------
    condição        pgsg_1 (5 sementes)   pgsg_2 (10 sementes)
    PGSGv2-lit      0.806                 0.7933 ± 0.0080
    PGSGv2-rand     0.76                  0.7983 ± 0.0077
    Δ_prior         +0.048                -0.005

A definição de 'rand' já foi descartada como causa: run_experiment_v2.py
linha 122 usa evaluate(..., prior=None), igual a pgsg_2.

USO
---
    python scripts/reconcile_prior_ablation.py --pgsg1-root ~/Dropbox/pgsg/pgsg_1
"""

from __future__ import annotations

import argparse
import csv as csvmod
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np

PUB = {
    "pgsg_1": {"lit": 0.806, "rand": 0.76},
    "pgsg_2": {"lit": 0.7933, "lit_sd": 0.0080, "rand": 0.7983, "rand_sd": 0.0077},
}

SEP = "=" * 74


def head(t):
    print(f"\n{SEP}\n{t}\n{SEP}")


def carregar_modulo(path: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def achar_csv(root: Path) -> Path | None:
    achados = []
    for pat in ("*angoDMC*.csv", "*mango*.csv", "*Mango*.csv", "*dmc*.csv", "*DMC*.csv"):
        achados.extend(root.rglob(pat))
    achados = [a for a in achados if ".git" not in a.parts]
    return max(achados, key=lambda p: p.stat().st_size) if achados else None


def wl_efetivos(pp, wl_orig: np.ndarray, p_novo: int) -> np.ndarray:
    """Descobre quais comprimentos de onda sobreviveram ao drop de bandas.

    O Preprocessor guarda o estado em .params; os nomes de chave variam, então
    procuramos um vetor booleano de tamanho p_orig ou um vetor de índices de
    tamanho p_novo. Falha ruidosamente em vez de adivinhar.
    """
    if p_novo == len(wl_orig):
        return wl_orig
    params = getattr(pp, "params", None)
    params = params() if callable(params) else params
    if isinstance(params, dict):
        itens = params.items()
    else:
        itens = [(k, getattr(params, k)) for k in dir(params) if not k.startswith("_")]
    for chave, val in itens:
        try:
            arr = np.asarray(val)
        except Exception:
            continue
        if arr.dtype == bool and arr.shape == wl_orig.shape and int(arr.sum()) == p_novo:
            print(f"    máscara de bandas: params['{chave}'] (booleana)")
            return wl_orig[arr]
        if arr.ndim == 1 and np.issubdtype(arr.dtype, np.integer) and arr.shape[0] == p_novo:
            if arr.max() < len(wl_orig):
                print(f"    máscara de bandas: params['{chave}'] (índices)")
                return wl_orig[arr]
    raise SystemExit(
        f"não foi possível localizar a máscara de bandas em Preprocessor.params "
        f"(p {len(wl_orig)} -> {p_novo}). Chaves: "
        + ", ".join(str(k) for k, _ in itens)
    )


def split_estratificado(y, frac_teste=0.2, seed=42, n_estratos=5):
    rng = np.random.default_rng(seed)
    q = np.quantile(y, np.linspace(0, 1, n_estratos + 1)[1:-1])
    estrato = np.digitize(y, q)
    idx_teste = []
    for e in np.unique(estrato):
        idx = np.flatnonzero(estrato == e)
        rng.shuffle(idx)
        idx_teste.append(idx[: int(round(frac_teste * len(idx)))])
    idx_teste = np.sort(np.concatenate(idx_teste))
    mask = np.ones(len(y), dtype=bool)
    mask[idx_teste] = False
    return np.flatnonzero(mask), idx_teste


def r2(y_true, y_pred):
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def resumo(v):
    v = np.asarray(v, dtype=float)
    return v.mean(), (v.std(ddof=1) if len(v) > 1 else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg1-root", default="~/Dropbox/pgsg/pgsg_1")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--season", type=int, default=4)
    ap.add_argument("--all-seasons", default="1,2,3,4,5",
                    help="temporadas usadas como safety_datasets (união das bandas zeradas)")
    ap.add_argument("--model-file", default=None)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--split-seed", type=int, default=42)
    ap.add_argument("--out", default="results/reconcile_prior_ablation.csv")
    a = ap.parse_args()

    root = Path(os.path.expanduser(a.pgsg1_root))
    model_file = (Path(os.path.expanduser(a.model_file)) if a.model_file
                  else Path(__file__).resolve().parents[1] / "src/pgsg_3/m_model/pgsg_v2.py")

    head("Módulos e dados")
    mod_model = carregar_modulo(model_file, "pgsg_v2_reconc")
    sys.path.insert(0, str(root))
    mod_run = carregar_modulo(root / "run_experiment_v2.py", "run_experiment_v2_reconc")
    print(f"modelo : {model_file}")

    csv_path = Path(os.path.expanduser(a.csv)) if a.csv else achar_csv(root)
    if csv_path is None or not csv_path.exists():
        raise SystemExit(f"CSV do Mango não encontrado sob {root}; use --csv")
    print(f"csv    : {csv_path}")

    SpectralDataset = mod_model.SpectralDataset
    PGSGv2Model = mod_model.PGSGv2Model

    ds = mod_run.load_mango_dmc_v3(csv_path, keep_seasons=[a.season])
    X, y, wl = np.asarray(ds.X), np.asarray(ds.y), np.asarray(ds.wavelengths)
    meta = dict(getattr(ds, "metadata", {}) or {})
    print(f"dados  : X={X.shape}  temporada={a.season}")

    # safety: as demais temporadas, para a união das bandas zeradas (Opção C)
    outras = [int(s) for s in a.all_seasons.split(",") if int(s) != a.season]
    safety = []
    for s in outras:
        try:
            safety.append(mod_run.load_mango_dmc_v3(csv_path, keep_seasons=[s]))
        except Exception as e:
            print(f"    [temporada {s} não carregada: {type(e).__name__}]")
    print(f"safety : {len(safety)} temporada(s) {outras}")

    idx_tr, idx_te = split_estratificado(y, 0.2, a.split_seed)
    train_ds = SpectralDataset(X=X[idx_tr], y=y[idx_tr], wavelengths=wl, metadata=dict(meta))
    test_ds = SpectralDataset(X=X[idx_te], y=y[idx_te], wavelengths=wl, metadata=dict(meta))
    print(f"split  : treino={len(idx_tr)}  teste={len(idx_te)}  (seed={a.split_seed})")

    # espelha run_experiment_v2.py:80 — sem safety_datasets, normalize_target=False
    pp = mod_run.Preprocessor(drop_zero_bands=True, apply_snv=True, normalize_target=False)
    Xtr, ytr = pp.fit_transform(train_ds)
    Xte, yte = pp.transform(test_ds)
    Xtr, ytr, Xte, yte = map(np.asarray, (Xtr, ytr, Xte, yte))
    print(f"preproc: p {X.shape[1]} -> {Xtr.shape[1]}  (esperado 281)")
    if Xtr.shape[1] != 281:
        print("    !! p diferente de 281: o protocolo NÃO reproduz o de pgsg_1")

    wl_ef = np.asarray(pp.params.kept_wavelengths)
    prior = np.asarray(mod_run.make_literature_prior(wl_ef))
    print(f"prior  : shape={prior.shape}  min={prior.min():.3f}  max={prior.max():.3f}")
    if prior.shape[0] != Xtr.shape[1]:
        raise SystemExit("prior incompatível com X — verificar ordem preproc/prior")

    tr = SpectralDataset(X=Xtr, y=ytr, wavelengths=wl_ef, metadata=dict(meta))
    te = SpectralDataset(X=Xte, y=yte, wavelengths=wl_ef, metadata=dict(meta))

    inv = None

    head(f"Rodando 2 condições x {a.seeds} sementes")
    linhas = []
    for seed in range(a.seeds):
        for cond, p in (("lit", prior), ("rand", None)):
            m = PGSGv2Model(seed=seed)
            m.fit(tr, prior=p)
            pred = m.predict(te) if hasattr(m, "predict") else m.transform(te)
            pred = np.asarray(pred).ravel()
            yt = np.asarray(yte).ravel()
            if inv is not None:
                try:
                    pred, yt = np.asarray(inv(pred)).ravel(), np.asarray(inv(yt)).ravel()
                except Exception:
                    pass
            score = r2(yt, pred)
            linhas.append({"seed": seed, "condicao": cond, "r2": score})
            print(f"  seed={seed:2d}  {cond:5s}  R2={score:.4f}")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=["seed", "condicao", "r2"])
        w.writeheader()
        w.writerows(linhas)
    print(f"\nescrito: {out}")

    def por(cond, ate=None):
        return resumo([r["r2"] for r in linhas
                       if r["condicao"] == cond and (ate is None or r["seed"] < ate)])

    head("Reconciliação")
    lit5, s_lit5 = por("lit", 5)
    rnd5, s_rnd5 = por("rand", 5)
    lit10, s_lit10 = por("lit")
    rnd10, s_rnd10 = por("rand")

    print(f"{'':22s} {'lit':>18s} {'rand':>18s} {'Δ_prior':>10s}")
    print(f"{'pgsg_1 publicado':22s} {PUB['pgsg_1']['lit']:>18.4f} {PUB['pgsg_1']['rand']:>18.4f} "
          f"{PUB['pgsg_1']['lit'] - PUB['pgsg_1']['rand']:>+10.4f}")
    print(f"{'pgsg_2 publicado':22s} {PUB['pgsg_2']['lit']:>10.4f}±{PUB['pgsg_2']['lit_sd']:.4f} "
          f"{PUB['pgsg_2']['rand']:>10.4f}±{PUB['pgsg_2']['rand_sd']:.4f} "
          f"{PUB['pgsg_2']['lit'] - PUB['pgsg_2']['rand']:>+10.4f}")
    print(f"{'este, sementes 0-4':22s} {lit5:>10.4f}±{s_lit5:.4f} {rnd5:>10.4f}±{s_rnd5:.4f} "
          f"{lit5 - rnd5:>+10.4f}")
    print(f"{'este, sementes 0-9':22s} {lit10:>10.4f}±{s_lit10:.4f} {rnd10:>10.4f}±{s_rnd10:.4f} "
          f"{lit10 - rnd10:>+10.4f}")

    pares = {}
    for r in linhas:
        pares.setdefault(r["seed"], {})[r["condicao"]] = r["r2"]
    dif = np.array([pares[s]["lit"] - pares[s]["rand"] for s in sorted(pares)])
    print(f"\ndiferença pareada: média={dif.mean():+.4f}  SD={dif.std(ddof=1):.4f}")
    try:
        from scipy.stats import wilcoxon
        stat, pval = wilcoxon(dif)
        print(f"Wilcoxon pareado: W={stat:.1f}  p={pval:.4f}")
    except Exception as e:
        print(f"[Wilcoxon indisponível: {e}]")

    head("Leitura")
    print("  0-4 ≈ pgsg_1 e 0-9 ≈ pgsg_2    -> nº de sementes explica; suavizar conclusão de pgsg_1")
    print("  ambas ≈ pgsg_2, nenhuma ≈ 0.76 -> o 0.76 de pgsg_1 precisa ser reexecutado antes da R2")
    print("  nenhuma bate com nada          -> protocolo divergia (checar p e o split aninhado)")


if __name__ == "__main__":
    main()
