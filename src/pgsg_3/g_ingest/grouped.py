"""Grouped splits and a calibrated PLS relevance reference.

PROVENANCE
----------
The functions below are vendorized, without change of logic, from

    repo   : github.com/clarimar/pgsg2-nir-raman-gating
    commit : 63b0bd9
    files  : scripts/r1_h1_calibrated_pls.py  (splits, PLS calibration)
             scripts/r1_check_replicates.py   (fruit grouping)

They are the methods of "Gate Topology and Reproducibility of Prior-Guided
Spectral Gating Across Near-Infrared and Raman Spectroscopy" (accepted,
Chemometrics and Intelligent Laboratory Systems). They are copied rather
than imported so that pgsg_3 does not acquire a second repository as a
runtime dependency, and so that the exact protocol is pinned here.

WHY THEY ARE NEEDED HERE
------------------------
Two protocol facts established by that paper invalidate the random split
used in the August 2026 lambda sweeps:

1. The 1,448 NIR spectra of season 4 come from 725 fruits, 723 of them
   measured twice. A random split puts both spectra of a fruit on opposite
   sides, so held-out R^2 is optimistic and cross-validation rewards models
   that memorize samples.

2. With a PLS baseline whose number of latent variables is selected on the
   training partition (one-standard-error rule, H between 46 and 73), the
   gated model does NOT outperform PLS on these NIR data: paired
   dR^2 = -0.108 +/- 0.031 over ten grouped splits. The +0.23 advantage of
   the earlier work came from a fixed H=10 baseline.

The second fact is also what makes `pls_reference_relevance` worth having:
the absolute coefficients of a calibrated PLS are an operational reference
for band relevance that does not come from the prior, so the agreement of
the gate with it is a non-circular interpretability measure. Correlation
between gate and prior only measures adherence to the starting point.
"""

from __future__ import annotations

import numpy as np

# sklearn's PLSRegression(scale=True), as in pgsg_1's PLSModel, so that the
# calibrated baseline differs from the published one only in H.
PLS_SCALE = True

FRUIT_META = ["Set", "Season", "Region", "Date", "Type", "Cultivar",
              "Pop", "Temp", "DM"]


# ----------------------------------------------------------------- grouping
def fruit_groups(csv_path, season: int = 4) -> np.ndarray:
    """Fruit id per spectrum: runs of consecutive rows with identical metadata.

    Mango DMC v3 has no fruit-ID column. Replicate spectra of one fruit are
    consecutive rows sharing every metadata field and the dry-matter value.
    """
    import pandas as pd

    df = pd.read_csv(csv_path, usecols=FRUIT_META)
    df = df[df["Season"] == season].reset_index(drop=True)
    key = df.astype(str).agg("|".join, axis=1).to_numpy()
    return np.cumsum(np.r_[True, key[1:] != key[:-1]]) - 1


def check_alignment(groups: np.ndarray, y: np.ndarray, csv_path, season: int = 4) -> None:
    """Fail loudly if the CSV rows and the loader's ordering disagree.

    The grouping is positional, so a mismatch would silently assign the wrong
    fruit to every spectrum.
    """
    import pandas as pd

    df = pd.read_csv(csv_path, usecols=["Season", "DM"])
    dm = df[df["Season"] == season]["DM"].to_numpy(float)
    y = np.asarray(y).ravel()
    if len(dm) != len(y) or not np.allclose(dm, y):
        raise SystemExit(
            "CSV rows and the pgsg_1 loader are not aligned; fruit groups would "
            f"be meaningless (CSV n={len(dm)}, loader n={len(y)})."
        )
    if len(groups) != len(y):
        raise SystemExit(f"groups n={len(groups)} != samples n={len(y)}")


def group_split(groups, test_frac: float, seed: int):
    """Random split of whole groups into (train_idx, test_idx)."""
    groups = np.asarray(groups)
    u = np.unique(groups)
    rng = np.random.default_rng(seed)
    rng.shuffle(u)
    test_groups = u[: int(round(test_frac * len(u)))]
    is_test = np.isin(groups, test_groups)
    return np.flatnonzero(~is_test), np.flatnonzero(is_test)


def group_folds(groups, n_folds: int, seed: int):
    """K folds of whole groups, groups shuffled then assigned round-robin."""
    groups = np.asarray(groups)
    u = np.unique(groups)
    rng = np.random.default_rng(seed)
    rng.shuffle(u)
    fold_of = {g: i % n_folds for i, g in enumerate(u)}
    f = np.array([fold_of[g] for g in groups])
    return [(np.flatnonzero(f != k), np.flatnonzero(f == k)) for k in range(n_folds)]


# ------------------------------------------------------- calibrated PLS
def _truncated_predict(model, X, h: int):
    """Predict with the first h components of a fitted sklearn PLSRegression.

    NIPALS extracts components sequentially and P^T W is upper triangular, so
    the h-component model equals the truncation of a larger model.
    """
    W = model.x_weights_[:, :h]
    P = model.x_loadings_[:, :h]
    Q = model.y_loadings_[:, :h]
    R = W @ np.linalg.pinv(P.T @ W)
    Xc = (X - model._x_mean) / model._x_std
    return (Xc @ R @ Q.T).ravel() * model._y_std.ravel()[0] + model._y_mean.ravel()[0]


def pls_cv_curve(X, y, h_max: int, n_folds: int, seed: int, groups=None):
    """(hs, mean_mse, se_mse) of K-fold CV over H = 1..h_max.

    One PLS model with h_max components is fitted per fold; smaller H come
    from truncation (exact for NIPALS), which makes large grids cheap.
    """
    from sklearn.cross_decomposition import PLSRegression
    from sklearn.model_selection import KFold

    h_max = int(min(h_max, X.shape[1], X.shape[0] - X.shape[0] // n_folds - 1))
    hs = np.arange(1, h_max + 1)
    if groups is None:
        folds = list(KFold(n_splits=n_folds, shuffle=True, random_state=seed).split(X))
    else:
        folds = group_folds(groups, n_folds, seed)
    fold_mse = np.zeros((n_folds, h_max))
    for k, (tr, va) in enumerate(folds):
        m = PLSRegression(n_components=h_max, scale=PLS_SCALE).fit(X[tr], y[tr])
        for j, h in enumerate(hs):
            fold_mse[k, j] = np.mean((y[va] - _truncated_predict(m, X[va], int(h))) ** 2)
    mean = fold_mse.mean(axis=0)
    se = fold_mse.std(axis=0, ddof=1) / np.sqrt(n_folds)
    return hs, mean, se


def select_h(hs, mean, se):
    """(h_cvmin, h_1se) by the minimum-error and one-standard-error rules."""
    j_min = int(np.argmin(mean))
    h_cvmin = int(hs[j_min])
    threshold = mean[j_min] + se[j_min]
    h_1se = int(hs[np.flatnonzero(mean <= threshold)[0]])
    return h_cvmin, h_1se


def fit_pls(X, y, h: int):
    from sklearn.cross_decomposition import PLSRegression
    return PLSRegression(n_components=int(h), scale=PLS_SCALE).fit(X, y)


def pls_reference_relevance(X_tr, y_tr, groups_tr=None, *, h_max: int = 120,
                            n_folds: int = 5, seed: int = 42) -> dict:
    """Band relevance from a PLS calibrated on the TRAINING partition only.

    Returns the absolute regression coefficients, which serve as an
    operational reference for which bands carry the signal. Unlike the prior,
    this reference is derived from the data, so agreement between the gate
    and it is not guaranteed by construction.

    Calibration uses grouped CV folds when `groups_tr` is given, otherwise
    plain K-fold; H is chosen by the one-standard-error rule.
    """
    X_tr = np.asarray(X_tr, dtype=float)
    y_tr = np.asarray(y_tr, dtype=float).ravel()
    hs, mean, se = pls_cv_curve(X_tr, y_tr, h_max, n_folds, seed, groups=groups_tr)
    h_cvmin, h_1se = select_h(hs, mean, se)
    model = fit_pls(X_tr, y_tr, h_1se)
    coef = np.abs(np.asarray(model.coef_).ravel())
    if coef.shape[0] != X_tr.shape[1]:          # sklearn changed coef_ orientation
        coef = np.abs(np.asarray(model.coef_).T.ravel())
    return {
        "relevance": coef,
        "h_1se": h_1se,
        "h_cvmin": h_cvmin,
        "h_max_effective": int(hs[-1]),
        "at_boundary": bool(h_cvmin == int(hs[-1])),
        "model": model,
    }
