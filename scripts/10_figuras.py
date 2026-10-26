#!/usr/bin/env python
"""Figures 1, 2 and 3, and an inventory of what Figures 4 and 5 would need.

PRESENTATION RULES, from the programme's standing constraints
-------------------------------------------------------------
No titles on any plot. Identification goes in the caption, which lives in the
manuscript and not in the image. Panel letters are kept because they are how a
caption refers to a panel, and they are not titles.

Vector output (PDF) at a width that survives a two-column layout.

Figure 3 carries two constraints set by the author on 2026-10-25:

  * the horizontal axis n is SHARED across the three panels, so the comparison
    is one of slope, but the vertical axes are INDEPENDENT, because a Jaccard
    index and a displacement correlation are different statistics and a shared
    vertical scale would imply an equivalence that does not hold;
  * nothing in the figure represents the association with n as causal. Seven
    sample sizes support a statement about sensitivity, not an identification
    of the mechanism behind the growth.

WHAT THIS SCRIPT COMPUTES AND WHAT IT TAKES ON TRUST
----------------------------------------------------
Everything in Figures 1 and 3 is computed here from
`data/processed/gates_r2/gates_n*.npz`.

Figure 2 needs one pair of numbers this repository does not hold: the overlap
of the accepted study's own NIR cell, 0.9418, and its collapse under randomised
tie resolution, 0.7005 +- 0.0068, at that codebase's convention q = 28. Those
come from findings/F002 and are passed as constants, marked in the code. Every
other point in Figure 2 is computed.

Figures 4 and 5 need files whose internal layout is not documented in this
repository, so this script does NOT guess at it. It reports what it found
under --results and --raman so the layout can be read off a real run.

USAGE
-----
    cd ~/pgsg/pgsg_3
    python scripts/10_figuras.py \
        --dir data/processed/gates_r2 \
        --results results \
        --raman results/raman_h12 \
        --out paper/figuras
"""

from __future__ import annotations

import argparse
import itertools
import json
from math import comb
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------- constantes
# findings/F002, braco NIR do artigo aceito, convencao q = 28 do codigo
# publicado. NAO sao recomputados aqui: aquela execucao nao esta neste
# repositorio. Qualquer outro ponto das figuras e computado.
PUB_J_SORT = 0.9418
PUB_J_RAND = 0.7005
PUB_J_RAND_SD = 0.0068
PUB_Q = 28

PLATO_TOL = 1e-9
SORTEIOS = 200


def esperanca_exata(q: int, L: int) -> float:
    """E[J] for two independent uniform q-subsets of L tied bands.

    Not q/(2L-q): that is J at the expected overlap, and J is strictly convex,
    so Jensen makes it a strict lower bound. findings/F002, 2026-10-25.
    """
    if L < q or q < 1:
        return float("nan")
    tot = comb(L, q)
    return float(sum(comb(q, k) * comb(L - q, q - k) / tot * k / (2 * q - k)
                     for k in range(max(0, 2 * q - L), q + 1)))


def jaccard_sort(gates: np.ndarray, q: int) -> float:
    tops = [set(np.argsort(g)[::-1][:q].tolist()) for g in gates]
    return float(np.mean([len(a & b) / len(a | b)
                          for a, b in itertools.combinations(tops, 2)]))


def jaccard_sorteado(gates: np.ndarray, q: int, seed: int = 0) -> tuple:
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(SORTEIOS):
        tops = [set(np.lexsort((rng.random(len(g)), -g))[:q].tolist())
                for g in gates]
        vals.append(np.mean([len(a & b) / len(a | b)
                             for a, b in itertools.combinations(tops, 2)]))
    v = np.asarray(vals)
    return float(v.mean()), float(v.std(ddof=1))


def corr_pares(mat: np.ndarray, posto: bool) -> tuple:
    from scipy.stats import rankdata
    X = np.apply_along_axis(rankdata, 1, mat) if posto else mat
    v = []
    for i, j in itertools.combinations(range(len(X)), 2):
        a, b = X[i], X[j]
        if a.std() > 1e-15 and b.std() > 1e-15:
            v.append(float(np.corrcoef(a, b)[0, 1]))
    v = np.asarray(v)
    return float(v.mean()), float(v.std(ddof=1) if v.size > 1 else 0.0)


def carregar(d: Path) -> dict:
    """The seven training sizes, keyed by n."""
    saida = {}
    for p in sorted(d.glob("gates_n*.npz")):
        n = int(p.stem.split("gates_n")[1])
        z = np.load(p, allow_pickle=False)
        saida[n] = {k: np.asarray(z[k], float) for k in z.files}
    return dict(sorted(saida.items()))


# ------------------------------------------------------------------- figuras

def silenciar() -> None:
    """fontTools logs every glyph it subsets and the Raman loader logs every
    HTTP head request. Two hundred lines of that buries the four lines that
    matter, and a buried verification is one nobody reads."""
    import logging
    for nome in ("fontTools", "fontTools.subset", "fontTools.ttLib",
                 "matplotlib.font_manager", "httpx", "huggingface_hub",
                 "huggingface_hub.utils._http", "datasets", "urllib3"):
        logging.getLogger(nome).setLevel(logging.ERROR)


def estilo():
    import matplotlib
    matplotlib.use("Agg")
    silenciar()
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
        "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "lines.linewidth": 1.0, "lines.markersize": 3.5,
        "legend.frameon": False, "pdf.fonttype": 42,
    })
    return plt


def figura1(dados: dict, out: Path) -> None:
    """The prior as a step function, its plateau, and q at both conventions.

    No in-plot description: the identification belongs to the caption. Level
    counts sit below their own step, and the plateau is marked by shading plus
    one short line of text in a corner the data cannot reach.
    """
    plt = estilo()
    z = next(iter(dados.values()))
    wl, prior = z["wavelengths"], z["prior"]
    o = np.argsort(wl)
    wl, prior = wl[o], prior[o]
    plato = prior >= prior.max() - PLATO_TOL

    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    ax.step(wl, prior, where="mid", color="0.15")
    ax.fill_between(wl, 0, prior, where=plato, step="mid",
                    color="0.15", alpha=0.15, linewidth=0)
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("prior $s$")
    ax.set_ylim(0, 1.18)

    niveis, contagens = np.unique(prior, return_counts=True)
    for v, c in zip(niveis, contagens):
        # Above the step, at the midpoint of the level's LONGEST CONTIGUOUS
        # RUN -- not at the mean of its wavelengths. A level with disjoint
        # runs, which the floor is, has a mean that can fall in a gap: on the
        # real axis the floor's mean lands near 690 nm, inside the 680-700
        # window, so the count was printed on top of that spike.
        onde = np.flatnonzero(prior == v)
        cortes = np.flatnonzero(np.diff(onde) > 1)
        trechos = np.split(onde, cortes + 1)
        maior = max(trechos, key=len)
        ax.annotate(f"{c}", xy=(wl[maior].mean(), v),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=6, color="0.35")
    # Top left, in two lines. The bottom strip is NOT free: on the real axis
    # (309-1149 nm) the floor's own count sits there, and a single long line
    # also ran past the left spine and under the y label.
    ax.text(0.02, 0.97,
            f"shaded: the prior's maximum, {plato.sum()} bands\n"
            f"top-decile size q = {PUB_Q} or 29",
            transform=ax.transAxes, va="top", ha="left", fontsize=6.5,
            color="0.3", linespacing=1.5)
    fig.savefig(out / "fig1_prior_degrau.pdf")
    plt.close(fig)
    print(f"  fig1: levels {dict(zip(niveis.round(3), contagens))}, "
          f"plateau {plato.sum()}, axis {wl.min():.0f}-{wl.max():.0f} nm")


def figura2(dados: dict, out: Path, q_dados: int) -> None:
    """Overlap by the sort, overlap with ties randomised, and exact chance."""
    plt = estilo()
    ns = list(dados)
    L = None
    sort_v, rand_v, rand_sd = [], [], []
    for n in ns:
        z = dados[n]
        prior = z["prior"]
        plato = np.flatnonzero(prior >= prior.max() - PLATO_TOL)
        L = len(plato)
        g = z["gates_lit"]
        sort_v.append(jaccard_sort(g, q_dados))
        m, s = jaccard_sorteado(g, q_dados)
        rand_v.append(m)
        rand_sd.append(s)
    acaso = esperanca_exata(q_dados, L)

    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    x = np.arange(len(ns) + 1)
    rot = [f"{n}" for n in ns] + ["accepted\nstudy"]
    ax.plot(x[:-1], sort_v, "o-", color="0.15", label="ties left to the sort")
    ax.errorbar(x[:-1], rand_v, yerr=rand_sd, fmt="s--", color="0.45",
                capsize=2, label="ties resolved at random")
    # the published cell, at its own convention q = 28 -- see module constants
    ax.plot([x[-1]], [PUB_J_SORT], "o", color="0.15", mfc="white")
    ax.errorbar([x[-1]], [PUB_J_RAND], yerr=[PUB_J_RAND_SD], fmt="s",
                color="0.45", mfc="white", capsize=2)
    ax.axhline(acaso, color="0.6", lw=0.8, ls=":")
    ax.axvline(x[-1] - 0.5, color="0.85", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(rot, fontsize=6)
    ax.set_xlabel("training size $n$")
    ax.set_ylabel("pairwise Jaccard")
    ax.set_ylim(0, 1.0)
    # The chance level goes in the legend, not on the plot: the randomised
    # series lands ON that line -- which is the result -- so any inline label
    # sits on top of the data by construction.
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([], [], color="0.15", marker="o", ls="-",
               label="ties left to the sort"),
        Line2D([], [], color="0.45", marker="s", ls="--",
               label="ties resolved at random"),
        Line2D([], [], color="0.6", ls=":",
               label=f"exact E[J] = {acaso:.4f} at q = {q_dados}"),
        Line2D([], [], color="0.3", marker="o", ls="none", mfc="white",
               label=f"open markers: published cell, q = {PUB_Q}"),
    ], loc="lower left", bbox_to_anchor=(0.0, 0.02))
    fig.savefig(out / "fig2_colapso_por_desempate.pdf")
    plt.close(fig)
    print(f"  fig2: sort {min(sort_v):.4f}-{max(sort_v):.4f}, "
          f"random {min(rand_v):.4f}-{max(rand_v):.4f}, E[J] {acaso:.4f}")


def figura3(dados: dict, out: Path, q_dados: int) -> None:
    """Three panels against a shared n, with INDEPENDENT vertical axes.

    The author's constraint of 2026-10-25: a Jaccard index and a displacement
    correlation are different statistics, so a shared vertical scale would
    imply an equivalence that does not hold. Nothing here represents the
    association with n as causal.
    """
    plt = estilo()
    ns = np.array(list(dados), float)
    j_rand, j_lit = [], []
    d_all, d_out, d_all_sd, d_out_sd = [], [], [], []
    for n in dados:
        z = dados[n]
        prior = z["prior"]
        plato = np.flatnonzero(prior >= prior.max() - PLATO_TOL)
        fora = np.setdiff1d(np.arange(len(prior)), plato)
        j_rand.append(jaccard_sort(z["gates_rand"], q_dados))
        j_lit.append(jaccard_sort(z["gates_lit"], q_dados))
        desl = z["gates_lit"] - prior
        m, s = corr_pares(desl, posto=True)
        d_all.append(m); d_all_sd.append(s)
        m, s = corr_pares(desl[:, fora], posto=True)
        d_out.append(m); d_out_sd.append(s)

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5), sharex=True)
    for ax, (y, lab) in zip(axes[:2], ((j_rand, "a"), (j_lit, "b"))):
        ax.plot(ns, y, "o-", color="0.15")
        ax.set_ylabel("pairwise Jaccard")
        # no in-plot description: it collides with the panel letter and the
        # identification belongs to the caption
        # limits from the data, never hard-coded: a fixed window that happens
        # to fit today clips silently when the numbers move
        lo, hi = min(y), max(y)
        folga = max(0.02, 0.12 * (hi - lo))
        ax.set_ylim(max(0.0, lo - folga), min(1.0, hi + folga))

    ax = axes[2]
    ax.errorbar(ns, d_all, yerr=d_all_sd, fmt="o-", color="0.15",
                capsize=2, label="all 281 bands")
    ax.errorbar(ns, d_out, yerr=d_out_sd, fmt="s--", color="0.45",
                capsize=2, label="plateau excluded")
    ax.set_ylabel("displacement correlation")
    # below the panel, outside the data area: both series rise across n, so
    # no interior corner is reliably free
    leg_h, leg_l = ax.get_legend_handles_labels()

    for i, ax in enumerate(axes):
        ax.set_xscale("log")
        ax.set_xticks(ns)
        # rotated: on a log axis 700 and 1158 are close enough that the two
        # labels merged into "7001158" in all three panels
        ax.set_xticklabels([f"{int(v)}" for v in ns], fontsize=6,
                           rotation=45, ha="right")
        ax.minorticks_off()
        ax.set_xlabel("training size $n$")
        # outside the axes, above left: inside it collides with the y label
        # at the axes' own left edge, above the box: further left and it
        # lands on the rotated y label, which panel (c) makes long
        ax.text(0.0, 1.10, "(" + "abc"[i] + ")", transform=ax.transAxes,
                fontsize=8, va="top", ha="left")
    fig.subplots_adjust(wspace=0.42, bottom=0.30)
    fig.legend(leg_h, leg_l, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.02))
    fig.savefig(out / "fig3_resposta_ao_tamanho.pdf")
    plt.close(fig)
    print(f"  fig3a: {min(j_rand):.4f}-{max(j_rand):.4f}   "
          f"fig3b: {min(j_lit):.4f}-{max(j_lit):.4f}")
    print(f"  fig3c: all {d_all[0]:.4f}..{d_all[-1]:.4f}   "
          f"outside {d_out[0]:.4f}..{d_out[-1]:.4f}")


# ------------------------------------------------------- figuras 4 e 5

def carregar_modulo(path: Path, nome: str):
    """Same mechanism 07 uses to borrow a tested function from 02."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location(nome, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def prior_raman(pgsg1_root: Path, pgsg2_root: Path, raman: Path) -> tuple:
    """Rebuild the Raman prior and its shift axis, and CHECK the rebuild.

    The loading chain lives inside `07_raman_lambda1.py`'s main() and is not
    factored out, so the four lines below duplicate it. Duplication can drift,
    so the result is verified against what the registered run itself recorded
    in cells.json -- the number of distinct prior values and the size of its
    plateau. A mismatch raises instead of drawing a prior that is not the one
    the finding was computed on.

    Note the argument order of 07's importer: (pgsg1_root, pgsg2_root).
    """
    r07 = carregar_modulo(Path(__file__).resolve().parent
                          / "07_raman_lambda1.py", "r07")
    mods = r07.importar(pgsg1_root, pgsg2_root)
    ds2 = mods["Loader"]().load()
    ds2 = mods["Prep"]().fit_transform(ds2)
    ds = mods["to_pgsg1"](ds2, target_unit="unknown")
    tr, _ = r07.dividir(ds, mods["DS"], 0)      # bands are split-invariant
    prior = np.asarray(mods["Prior"]().compute(tr.wavelengths), float)
    eixo = np.asarray(tr.wavelengths, float)

    cel = json.loads((raman / "cells.json").read_text())
    ref = next((v for k, v in cel.items()
                if k.startswith("0|literature|")), None)
    if ref is not None:
        niveis = int(len(np.unique(prior)))
        plato = int((prior >= prior.max() - PLATO_TOL).sum())
        if niveis != int(ref["niveis"]) or plato != int(ref["plato"]):
            raise SystemExit(
                f"the rebuilt Raman prior does not match the registered run: "
                f"rebuilt has {niveis} distinct values and a plateau of "
                f"{plato}, cells.json records {ref['niveis']} and "
                f"{ref['plato']}. Figure 4 panel (a) would not be showing the "
                f"prior the finding was computed on. Resolve this before "
                f"drawing it.")
        print(f"  fig4 panel (a): rebuilt prior verified against cells.json "
              f"({niveis} distinct values, plateau {plato})")
    return prior, eixo


def figura4(raman: Path, out: Path, prior=None, eixo=None) -> None:
    """Panel (a) the continuous Raman prior; panel (b) the overlap by the sort
    against the overlap with ties randomised, in the three partitions.

    Panel (b) reads `cells.json`, which already stores j_index, j_random and
    j_random_sd: nothing is recomputed, so the figure cannot disagree with the
    finding it illustrates. Panel (a) needs the Raman shift axis, which only
    the loader has; when the prior is not supplied the panel is OMITTED and
    said to be, rather than drawn from an invented axis.
    """
    plt = estilo()
    celulas = json.loads((raman / "cells.json").read_text())
    # keys are "<partition>|<arm>|<lam>"; the registered arm is literature and
    # lam = 1 is fixed by the pre-registration, not chosen from the data
    lit = {int(k.split("|")[0]): v for k, v in celulas.items()
           if k.split("|")[1] == "literature" and k.split("|")[2] == "1"}
    if not lit:
        raise SystemExit(f"{raman}/cells.json: no literature cell at lam=1 "
                         f"(keys like {list(celulas)[:3]})")
    parts = sorted(lit)

    ncols = 2 if prior is not None else 1
    fig, axes = plt.subplots(1, ncols, figsize=(3.5 * ncols + 0.3, 2.3))
    axes = np.atleast_1d(axes)
    k = 0
    if prior is not None:
        ax = axes[0]; k = 1
        o = np.argsort(eixo)
        ax.plot(np.asarray(eixo)[o], np.asarray(prior)[o], color="0.15", lw=0.7)
        pico = np.flatnonzero(prior >= prior.max() - PLATO_TOL)
        ax.plot(np.asarray(eixo)[pico], np.asarray(prior)[pico], "o",
                color="0.15", ms=3)
        ax.set_xlabel("Raman shift (cm$^{-1}$)")
        ax.set_ylabel("prior $s$")
        ax.text(0.98, 0.95,
                f"{len(np.unique(prior))} distinct values\n"
                f"maximum at {len(pico)} band" + ("s" if len(pico) != 1 else ""),
                transform=ax.transAxes, ha="right", va="top", fontsize=6.5,
                color="0.3", linespacing=1.4)

    ax = axes[k]
    x = np.arange(len(parts))
    ji = [lit[q]["j_index"] for q in parts]
    jr = [lit[q]["j_random"] for q in parts]
    sd = [lit[q]["j_random_sd"] for q in parts]
    ax.plot(x, ji, "o-", color="0.15", label="ties left to the sort")
    ax.errorbar(x, jr, yerr=sd, fmt="s--", color="0.45", capsize=2,
                label="ties resolved at random")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{q}" for q in parts])
    ax.set_xlabel("partition")
    ax.set_ylabel("pairwise Jaccard")
    lo, hi = min(min(ji), min(jr)), max(max(ji), max(jr))
    folga = max(0.02, 0.15 * (hi - lo))
    ax.set_ylim(max(0.0, lo - folga), min(1.0, hi + folga))
    ax.legend(loc="lower left")

    # Letters only when both panels exist: with (a) omitted the survivor is
    # conceptually (b), and labelling it (a) would mislabel the caption.
    if ncols == 2:
        for idx, ax in enumerate(axes):
            ax.text(0.0, 1.10, "(" + "ab"[idx] + ")", transform=ax.transAxes,
                    fontsize=8, va="top", ha="left")
    fig.subplots_adjust(wspace=0.34)
    fig.savefig(out / "fig4_controle_raman.pdf")
    plt.close(fig)
    dif = [abs(a - b) for a, b in zip(ji, jr)]
    print(f"  fig4: partitions {parts}, sort {min(ji):.4f}-{max(ji):.4f}, "
          f"random {min(jr):.4f}-{max(jr):.4f}, max |diff| {max(dif):.4f}"
          + ("  (panel a omitted: no Raman prior supplied)"
             if prior is None else ""))


PARTICOES_FIG5 = tuple(range(5, 15))


def conferir_particoes(celulas: list[Path]) -> list[int]:
    """Exactly partitions 5 to 14, no gap and no duplicate.

    Author's requirement of 2026-10-25: a pattern search that happens to match
    ten cells today is not a guarantee, and Figure 5 is not complete on a
    silently accepted subset. This raises instead of drawing nine partitions
    and calling the figure done.
    """
    numeros = []
    for d in celulas:
        s = "".join(ch for ch in d.name if ch.isdigit())
        if not s:
            raise SystemExit(f"{d.name}: no partition number in the cell name. "
                             f"Pass --cells explicitly.")
        numeros.append(int(s))
    faltando = sorted(set(PARTICOES_FIG5) - set(numeros))
    sobrando = sorted(set(numeros) - set(PARTICOES_FIG5))
    dup = sorted({n for n in numeros if numeros.count(n) > 1})
    if faltando or sobrando or dup:
        raise SystemExit(
            "Figure 5 needs exactly partitions "
            f"{PARTICOES_FIG5[0]}..{PARTICOES_FIG5[-1]}.\n"
            f"  found    : {sorted(numeros)}\n"
            + (f"  MISSING  : {faltando}\n" if faltando else "")
            + (f"  EXTRA    : {sobrando}\n" if sobrando else "")
            + (f"  DUPLICATE: {dup}\n" if dup else "")
            + "The figure is not complete on a subset. Pass --cells "
              "explicitly if the discovery pattern is wrong.")
    print(f"  fig5: partitions verified, exactly "
          f"{PARTICOES_FIG5[0]}..{PARTICOES_FIG5[-1]}, no gap, no duplicate")
    return numeros


def figura5(celulas: list[Path], out: Path) -> None:
    """Within-level agreement between gate and PLS reference, by partition,
    distinguishing the prior's floor from its plateau.

    The computation is NOT reimplemented: `ler` and `h10_serie` come from
    `06_analise_plato.py`, the code that produced the finding. A figure that
    recomputes its own numbers can disagree with the text it illustrates.
    """
    plt = estilo()
    conferir_particoes(celulas)
    m = carregar_modulo(Path(__file__).resolve().parent
                        / "06_analise_plato.py", "r06")
    if m.LAM_FIXO != 1.0:
        raise SystemExit(f"06_analise_plato.LAM_FIXO is {m.LAM_FIXO}, not 1.0. "
                         f"The pre-registration fixes lambda = 1 for this "
                         f"result; the figure must not quietly use another.")
    linhas = {}
    for d in celulas:
        c = m.ler(d)
        prior, niveis = c["prior"], c["niveis"]
        piso = np.flatnonzero(prior <= niveis.min() + m.TOL_NIVEL)
        linhas[d.name] = {
            "piso": m.h10_serie(c, piso),
            "plato": m.h10_serie(c, c["plato"]),
            "n_piso": len(piso), "n_plato": len(c["plato"]),
            "min_banda": int(c["contagens"].min()),
        }

    nomes = list(linhas)
    x = np.arange(len(nomes))
    fig, ax = plt.subplots(figsize=(4.8, 2.4))
    for chave, fmt, cor, rot in (("piso", "o-", "0.15", "floor level"),
                                 ("plato", "s--", "0.5", "plateau level")):
        md = [float(np.mean(linhas[n][chave])) for n in nomes]
        sd = [float(np.std(linhas[n][chave], ddof=1)) for n in nomes]
        ax.errorbar(x, md, yerr=sd, fmt=fmt, color=cor, capsize=2, label=rot)
    ax.axhline(0.0, color="0.75", lw=0.8)
    ax.set_xticks(x)
    # partition numbers, not directory names: the cell's name is bookkeeping
    rot = ["".join(ch for ch in n if ch.isdigit()) or n for n in nomes]
    ax.set_xticklabels(rot)
    ax.set_xlabel("partition")
    ax.set_ylabel("within-level rank correlation")
    # below the axes: the floor series occupies the upper region wherever it
    # is positive, which is the result
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=2)
    fig.subplots_adjust(bottom=0.32)
    fig.savefig(out / "fig5_alinhamento_intra_nivel.pdf")
    plt.close(fig)
    for n in nomes:
        r = linhas[n]
        print(f"  fig5 {n:<18} floor {np.mean(r['piso']):+.4f} "
              f"({r['n_piso']} bands)   plateau {np.mean(r['plato']):+.4f} "
              f"({r['n_plato']} bands)")
    md_piso = np.array([np.mean(linhas[n]["piso"]) for n in nomes])
    md_plato = np.array([np.mean(linhas[n]["plato"]) for n in nomes])
    print(f"  fig5: floor positive in {int((md_piso > 0).sum())}/{len(nomes)}, "
          f"mean {md_piso.mean():+.4f};  plateau negative in "
          f"{int((md_plato < 0).sum())}/{len(nomes)}, mean "
          f"{md_plato.mean():+.4f}")
    menor = min(linhas[n]["min_banda"] for n in nomes)
    if menor < m.MIN_BANDAS_NIVEL:
        print(f"  fig5: the prior carries a level of {menor} bands, below "
              f"MIN_BANDAS_NIVEL = {m.MIN_BANDAS_NIVEL}. It is NOT plotted, "
              f"because 06_analise_plato reports such a level and never "
              f"interprets it.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/processed/gates_r2")
    ap.add_argument("--results", default="results")
    ap.add_argument("--raman", default="results/raman_h12")
    ap.add_argument("--out", default="paper/figuras")
    ap.add_argument("--decil", type=float, default=0.10)
    ap.add_argument("--cells", nargs="*", default=None,
                    help="cells for Figure 5, as 08_analise_condicional takes "
                         "them. Without this they are discovered under "
                         "--results and the matches are printed.")
    ap.add_argument("--pgsg2-root", default="",
                    help="the directory CONTAINING the pgsg2 package. Needed "
                         "only for Figure 4 panel (a); without it the panel "
                         "is omitted and said to be.")
    ap.add_argument("--pgsg1-root", default="")
    a = ap.parse_args()

    d = Path(a.dir).expanduser()
    dados = carregar(d)
    if not dados:
        raise SystemExit(f"no gates_n*.npz in {d}")
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    p = len(next(iter(dados.values()))["prior"])
    q = max(1, int(np.ceil(a.decil * p)))
    print(f"{len(dados)} training sizes: {list(dados)}")
    print(f"p = {p}, q = ceil({a.decil}*p) = {q}  "
          f"(the published ablation uses floor division, q = {PUB_Q})")
    print("\nwriting figures:")
    figura1(dados, out)
    figura2(dados, out, q)
    figura3(dados, out, q)
    print(f"\n  -> {out}/fig1_prior_degrau.pdf")
    print(f"  -> {out}/fig2_colapso_por_desempate.pdf")
    print(f"  -> {out}/fig3_resposta_ao_tamanho.pdf")
    print("\nNo plot carries a title. Identification belongs in the caption.")
    print("Figure 2 takes two numbers on trust -- the accepted study's 0.9418")
    print("and its 0.7005 +- 0.0068 collapse, at q = 28 -- because that run is")
    print("not in this repository. They are module constants, marked as such.")

    raman = Path(a.raman).expanduser() if a.raman else None
    if raman and (raman / "cells.json").is_file():
        prior = eixo = None
        if a.pgsg2_root and a.pgsg1_root:
            try:
                prior, eixo = prior_raman(Path(a.pgsg1_root).expanduser(),
                                          Path(a.pgsg2_root).expanduser(),
                                          raman)
            except SystemExit:
                raise
            except Exception as e:                            # noqa: BLE001
                print(f"\n  fig4 panel (a): omitted -- could not build the "
                      f"Raman prior ({type(e).__name__}: {e})")
        print()
        figura4(raman, out, prior, eixo)
        print(f"  -> {out}/fig4_controle_raman.pdf")
    else:
        print(f"\n  fig4 SKIPPED: {raman}/cells.json not found")

    celulas = [Path(c).expanduser() for c in a.cells] if a.cells else []
    if not celulas and a.results:
        celulas = sorted(
            (p for p in Path(a.results).expanduser().glob("p*")
             if (p / "gates.npz").is_file() and "_lit" in p.name),
            key=lambda p: int("".join(ch for ch in p.name if ch.isdigit()) or 0))
        print(f"\n  fig5 cells discovered under {a.results}: "
              f"{[p.name for p in celulas]}")
    if celulas:
        figura5(celulas, out)
        print(f"  -> {out}/fig5_alinhamento_intra_nivel.pdf")
    else:
        print("\n  fig5 SKIPPED: no cells found. Pass --cells explicitly, "
              "the way 08_analise_condicional takes them.")


if __name__ == "__main__":
    main()
