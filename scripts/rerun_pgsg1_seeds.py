#!/usr/bin/env python
"""
Reexecução do pgsg_1 com sementes de modelo genuínas.

PROBLEMA CORRIGIDO
------------------
Em run_experiment_v2.py (linhas ~99-118), as fábricas fixam seed=42:

    lambda: PGSGv2Model(hidden=32, max_epochs=500, patience=30, seed=42)

As "5 sementes" variam apenas a amostragem do subconjunto de treino
(StratifiedTrainSampler), nunca a inicialização do modelo. Em n_target =
tamanho do pool, o amostrador devolve sempre o mesmo conjunto e o split de
teste é fixo (seed=42) — logo as 5 réplicas são execuções IDÊNTICAS.

Verificado em results_v2/pred_results.csv, n_actual=1158: os 5 valores de r2
coincidem até o 6º decimal para os 5 modelos (PGSGv2=0.805524,
PGSGv2-random=0.757743). Em results/ (n=10243, n_target < pool) os valores
variam — mesmo código, confirmando o mecanismo.

Consequências no manuscrito: os IC bootstrap da última linha da Tabela 1 não
são intervalos (reamostragem de 5 cópias), e Δ_prior=+0.048 é uma medida
única contra outra, não média de 5 sementes.

O QUE ESTE SCRIPT FAZ
---------------------
Reexecuta o mesmo pipeline passando sc.seed às fábricas, de modo que cada
cenário tenha inicialização de modelo própria. Escreve um CSV no mesmo
formato de pred_results.csv e imprime a comparação com os valores publicados.

NÃO altera run_experiment_v2.py nem nada em pgsg_1 — só lê.

USO
---
    # ponto publicado, réplicas genuínas
    python scripts/rerun_pgsg1_seeds.py --n-grid 1159 --seeds 10

    # curva completa (demorado)
    python scripts/rerun_pgsg1_seeds.py \
        --n-grid 30,60,100,200,400,700,1159 --seeds 10
"""

from __future__ import annotations

import argparse
import csv as csvmod
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np

SEASON_DEFAULT = 4
PUB_N1159 = {"PGSGv2": 0.805524, "PGSGv2-random": 0.757743,
             "PLS": 0.568351, "MLP": 0.698979, "CNN1D-shallow": 0.706874}

SEP = "=" * 74


def head(t):
    print(f"\n{SEP}\n{t}\n{SEP}")


def carregar_modulo(path: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def achar_csv(root: Path):
    achados = []
    for pat in ("*angoDMC*.csv", "*mango*.csv", "*Mango*.csv", "*dmc*.csv", "*DMC*.csv"):
        achados.extend(root.rglob(pat))
    achados = [a for a in achados if ".git" not in a.parts]
    return max(achados, key=lambda p: p.stat().st_size) if achados else None


def r2(y_true, y_pred):
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def rmse(y_true, y_pred):
    return float(np.sqrt(((np.asarray(y_true).ravel() - np.asarray(y_pred).ravel()) ** 2).mean()))


def prever(modelo, ds):
    return np.asarray(modelo.predict(ds) if hasattr(modelo, "predict") else modelo.transform(ds)).ravel()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgsg1-root", default="~/Dropbox/pgsg/pgsg_1")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--model-file", default=None,
                    help="default: a cópia vendorizada em src/pgsg_3/m_model/pgsg_v2.py")
    ap.add_argument("--season", type=int, default=SEASON_DEFAULT)
    ap.add_argument("--n-grid", default="1159")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--out", default="results/rerun_pgsg1_seeds.csv")
    ap.add_argument("--baselines", action="store_true",
                    help="incluir PLS/MLP/CNN1D além das duas condições PGSGv2")
    a = ap.parse_args()

    root = Path(os.path.expanduser(a.pgsg1_root))
    model_file = (Path(os.path.expanduser(a.model_file)) if a.model_file
                  else Path(__file__).resolve().parents[1] / "src/pgsg_3/m_model/pgsg_v2.py")
    n_grid = [int(x) for x in a.n_grid.split(",")]
    seeds = list(range(a.seeds))

    head("Setup")
    mod_model = carregar_modulo(model_file, "pgsg_v2_rerun")
    sys.path.insert(0, str(root))
    mod = carregar_modulo(root / "run_experiment_v2.py", "run_experiment_v2_rerun")
    print(f"modelo : {model_file}")

    csv_path = Path(os.path.expanduser(a.csv)) if a.csv else achar_csv(root)
    if csv_path is None:
        raise SystemExit(f"CSV não encontrado sob {root}; use --csv")
    print(f"csv    : {csv_path}")
    print(f"n_grid : {n_grid}   sementes: {seeds}")

    SpectralDataset = mod_model.SpectralDataset
    PGSGv2Model = mod_model.PGSGv2Model

    # ---- dados: safra alvo, replicando run_experiment_v2.py:50-61
    ds_full = mod.load_mango_dmc_v3(csv_path)
    mask = np.asarray(ds_full.group_ids) == a.season
    ds4 = SpectralDataset(
        X=np.asarray(ds_full.X)[mask], y=np.asarray(ds_full.y)[mask],
        wavelengths=np.asarray(ds_full.wavelengths), metadata=dict(ds_full.metadata),
        group_ids=np.asarray(ds_full.group_ids)[mask],
    )
    print(f"safra {a.season}: n={ds4.X.shape[0]}, p_raw={ds4.X.shape[1]}")

    # ---- cenários: idêntico ao original
    gen = mod.ScenarioGenerator(
        test_strategy=mod.FixedFractionTest(fraction=0.2, seed=42),
        train_strategy=mod.StratifiedTrainSampler(),
        n_grid=n_grid,
        seeds=seeds,
    )
    gen.fit(ds4)
    cenarios = list(gen.iter_scenarios())
    print(f"cenários: {len(cenarios)}")

    head("Rodando (seed do modelo = seed do cenário)")
    linhas = []
    for i, sc in enumerate(cenarios, 1):
        prep = mod.Preprocessor(drop_zero_bands=True, apply_snv=True, normalize_target=False)
        X_tr, y_tr = prep.fit_transform(sc.train_dataset)
        X_te, y_te = prep.transform(sc.test_dataset)
        wl = prep.params.kept_wavelengths
        tr = SpectralDataset(X=X_tr, y=y_tr, wavelengths=wl,
                             metadata=dict(sc.train_dataset.metadata))
        te = SpectralDataset(X=X_te, y=y_te, wavelengths=wl,
                             metadata=dict(sc.test_dataset.metadata))
        prior = np.asarray(mod.make_literature_prior(wl))

        # AQUI está a correção: seed=sc.seed, não 42
        tarefas = [
            ("PGSGv2", lambda s=sc.seed: PGSGv2Model(hidden=32, max_epochs=500, patience=30, seed=s), prior),
            ("PGSGv2-random", lambda s=sc.seed: PGSGv2Model(hidden=32, max_epochs=500, patience=30, seed=s), None),
        ]
        if a.baselines:
            tarefas += [
                ("PLS", lambda: mod.PLSModel(n_components=10), None),
                ("MLP", lambda s=sc.seed: mod.MLPModel(hidden=64, max_epochs=500, patience=30, seed=s), None),
                ("CNN1D-shallow", lambda s=sc.seed: mod.CNN1DModel(depth="shallow", max_epochs=500, patience=30, seed=s), None),
            ]

        for nome, fab, pri in tarefas:
            m = fab()
            try:
                m.fit(tr, prior=pri)
            except TypeError:
                m.fit(tr)  # PLS e afins não aceitam prior
            pred = prever(m, te)
            linhas.append({
                "n_target": sc.n_target, "n_actual": sc.n_actual, "seed": sc.seed,
                "model_name": nome, "r2": r2(y_te, pred), "rmse": rmse(y_te, pred),
            })
            print(f"  [{i:>3}/{len(cenarios)}] n={sc.n_actual:<5} seed={sc.seed} "
                  f"{nome:<14} R2={linhas[-1]['r2']:.4f}  p={X_tr.shape[1]}")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csvmod.DictWriter(f, fieldnames=["n_target", "n_actual", "seed", "model_name", "r2", "rmse"])
        w.writeheader()
        w.writerows(linhas)
    print(f"\nescrito: {out}")

    # ---- resumo
    head("Réplicas agora são genuínas?")
    for n in sorted({r["n_actual"] for r in linhas}):
        print(f"\nn_actual = {n}")
        for nome in sorted({r["model_name"] for r in linhas}):
            v = [r["r2"] for r in linhas if r["n_actual"] == n and r["model_name"] == nome]
            if not v:
                continue
            arr = np.asarray(v)
            sd = arr.std(ddof=1) if len(arr) > 1 else 0.0
            flag = "  <-- DEGENERADO" if len(set(np.round(arr, 6))) == 1 and len(arr) > 1 else ""
            pub = PUB_N1159.get(nome)
            pubs = f"  publicado={pub:.4f}" if (pub is not None and n >= 1100) else ""
            print(f"  {nome:<15} média={arr.mean():.4f} ± {sd:.4f}  (n={len(arr)}){pubs}{flag}")

        lit = np.asarray([r["r2"] for r in linhas if r["n_actual"] == n and r["model_name"] == "PGSGv2"])
        rnd = np.asarray([r["r2"] for r in linhas if r["n_actual"] == n and r["model_name"] == "PGSGv2-random"])
        if len(lit) == len(rnd) and len(lit) > 1:
            dif = lit - rnd
            print(f"  Δ_prior pareado: {dif.mean():+.4f} ± {dif.std(ddof=1):.4f}")
            try:
                from scipy.stats import wilcoxon
                s, p = wilcoxon(dif)
                print(f"  Wilcoxon: W={s:.1f}  p={p:.4f}")
            except Exception:
                pass
            if n >= 1100:
                print(f"  publicado: Δ_prior = +0.0478 (medida única vs medida única)")

    head("Para a carta-resposta")
    print("  O Δ_prior e o SD acima substituem o valor de n=1 do manuscrito.")
    print("  Se o SD de PGSGv2-random for ~2x o de PGSGv2, isso é o mesmo efeito")
    print("  que o H4 de pgsg_2 mede por Jaccard: sem prior o gate é instável.")


if __name__ == "__main__":
    main()
