"""Distances between aircraft (Gower) and between firms (Jaffe proximity), nearest neighbours.

Pure functions: no config, no data dictionary. The caller says which fields are numeric and
supplies the weights.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional

import numpy as np
import pandas as pd


def subsystem_weights(fields: Iterable[str], subsystem_of: Mapping[str, str],
                      default: str = "propulsion") -> Dict[str, float]:
    """One unit of weight per subsystem, divided among its fields.

    w_f = 1 / (number of fields of f's subsystem); a field missing from `subsystem_of` falls in
    `default` ("propulsion", as the archive does).

    Ported from: archive/.../dataset_facts/a3.py:gower_distance (weighting == "subsystem")
    Used in: la_dd_q (main weighting, 5.3).
    """
    subs = {f: subsystem_of.get(f, default) for f in fields}
    size = pd.Series(subs).value_counts()
    return {f: 1.0 / size[s] for f, s in subs.items()}


def uniform_weights(fields: Iterable[str]) -> Dict[str, float]:
    """w_f = 1 for every field.

    Ported from: archive/.../dataset_facts/a3.py:gower_distance (weighting != "subsystem")
    Used in: la_dd_q (robustness weighting).
    """
    return {f: 1.0 for f in fields}


def gower_distance(frame: pd.DataFrame, fields: List[str], numeric: Iterable[str],
                   weights: Mapping[str, float]) -> np.ndarray:
    """Gower (1971) distance matrix between the rows of `frame`, with blanks left out of the average.

    d(i,j) = Σ_k w_k δ_ijk (1 − s_ijk) / Σ_k w_k δ_ijk
    δ_ijk = 1 if both rows carry a value for field k, else 0 (a pair with Σ w δ = 0 gives NaN);
    s_ijk = 1 − |x_ik − x_jk| / range_k for a numeric field (range over the frame; 0 difference if
            range = 0), and 1 if the categories match else 0 for a categorical field.

    Parameters: `fields`; `numeric` = names compared by range (all others by match);
    `weights` = field -> w_k (see subsystem_weights / uniform_weights).
    Ported from: archive/.../dataset_facts/a3.py:gower_distance
    Used in: la_dd_q (condition 3), nearest-neighbour checks (rule 4 sensitivity).
    """
    numeric = set(numeric)
    n = len(frame)
    num = np.zeros((n, n))
    den = np.zeros((n, n))
    for f in fields:
        x = frame[f]
        present = x.notna().to_numpy()
        both = present[:, None] & present[None, :]
        if f in numeric:
            a = pd.to_numeric(x, errors="coerce").to_numpy(dtype=float)
            rng = np.nanmax(a) - np.nanmin(a) if present.any() else 0.0
            diff = np.abs(a[:, None] - a[None, :]) / rng if rng > 0 else np.zeros((n, n))
        else:
            codes = pd.factorize(x.astype(object).where(x.notna(), None), use_na_sentinel=True)[0]
            diff = (codes[:, None] != codes[None, :]).astype(float)
        diff = np.where(both, diff, 0.0)
        num += weights[f] * diff
        den += weights[f] * both
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def nearest_neighbours(D: np.ndarray, ids: np.ndarray, tol: float = 1e-12) -> Dict[str, frozenset]:
    """Each row's nearest neighbours: every other row at the minimum distance (ties kept).

    NN(i) = { j != i : D_ij <= min_{k != i} D_ik + tol }; NaN distances count as infinite.

    Parameters: tol = 1e-12.
    Ported from: archive/.../dataset_facts/a3.py:nearest_neighbours
    Used in: rule-4 sensitivity (la_boom_wing_neighbours).
    """
    D = np.where(np.isnan(D), np.inf, D.copy())
    np.fill_diagonal(D, np.inf)
    m = D.min(axis=1, keepdims=True)
    near = D <= m + tol
    return {ids[i]: frozenset(ids[np.flatnonzero(near[i])]) for i in range(len(ids))}


def jaffe_proximity(profiles: pd.DataFrame) -> pd.DataFrame:
    """Jaffe (1986) technological proximity: cosine between the rows (firm profiles).

    P(a,b) = x_a · x_b / (|x_a| |x_b|)   (a zero row is left as zeros)

    Ported from: archive/.../dataset_facts/a2.py:proximity_matrix
    Used in: la_proximity_region, a2_d14_firm_proximity.
    """
    x = profiles.to_numpy(dtype=float)
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    unit = x / np.where(norm == 0, 1, norm)
    return pd.DataFrame(unit @ unit.T, index=profiles.index, columns=profiles.index)





def proximity_order(prox: pd.DataFrame) -> List[str]:
    """Firms ordered so that proximate firms sit together: the leaf order of an average-linkage clustering of 1 - proximity.

    RULE: d = (1 - P) clipped at 0 with a zero diagonal; scipy ``linkage(squareform(d), "average")``; ``leaves_list``. The input order of the
    firms decides ties; the order is part of the document's reproducibility (the permutation test of regional.region_proximity_test draws
    its shuffles over this order). The firms' original order is returned if the clustering fails.

    Ported from: archive/.../dataset_facts/a2.py:proximity_order
    Used in: la_proximity_region.
    """
    try:
        from scipy.cluster.hierarchy import leaves_list, linkage
        from scipy.spatial.distance import squareform
        d = (1 - prox.to_numpy()).clip(min=0)
        np.fill_diagonal(d, 0)
        return list(prox.index[leaves_list(linkage(squareform(d, checks=False), "average"))])
    except Exception:
        return list(prox.index)
