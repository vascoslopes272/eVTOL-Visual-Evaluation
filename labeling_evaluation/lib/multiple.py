"""Multiple-testing adjustment of a family of p values (supervisor review 2, 2026-10).

Pure functions: arrays / Series in, arrays / Series out.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests


def holm(p) -> np.ndarray:
    """Holm step-down adjusted p values of ONE family (statsmodels multipletests, method='holm').

    The family is the finite values of ``p``; a NaN (a test that could not run) is left NaN and does not count in the family.
    Returns an array aligned with ``p``.
    Used in: viz/thesis_q6.py (II.1), viz/analysis3.py (III.1), viz/thesis_q4.py (I.2), viz/frames.py (V regional tests).
    """
    p = np.asarray(p, dtype=float)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    if ok.any():
        out[ok] = multipletests(p[ok], method="holm")[1]
    return out


def holm_by(frame: pd.DataFrame, p_col: str, family_cols) -> pd.Series:
    """:func:`holm` within each family, the families being the groups of ``family_cols`` (a list, or [] for one family)."""
    if not family_cols:
        return pd.Series(holm(frame[p_col]), index=frame.index)
    out = pd.Series(np.nan, index=frame.index)
    for _, g in frame.groupby(list(family_cols), sort=False, dropna=False):
        out.loc[g.index] = holm(g[p_col])
    return out
