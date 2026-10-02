"""Concentration of aircraft over filers / firms / classes (science only)."""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np
import pandas as pd


def shares(labels: pd.Series) -> pd.Series:
    """Share of each distinct non-null label, largest first.

    Formula: s_i = n_i / sum n.
    Ported from: metrics.py:hhi / top_k_share (value_counts(normalize=True))
    """
    return labels.dropna().value_counts(normalize=True)


def hhi(labels: pd.Series) -> float:
    """Herfindahl-Hirschman index of a column of filer labels: the sum of squared shares.

    Formula: HHI = sum_i s_i^2, s_i = share of label i among non-null labels (range 1/k .. 1).
    Ported from: metrics.py:hhi
    Used in: la_d8_concentration / a2_d8_concentration ('hhi')
    """
    p = labels.dropna().value_counts(normalize=True)
    return float((p ** 2).sum())


def inverse_hhi(counts) -> float:
    """Effective number of equally sized units, 1/HHI (the "effective filers" of the document).
    NOT diversity.effective_number, which is exp(entropy), the Hill number of order 1.

    Formula: N_eff = 1 / sum_i p_i^2, p_i = n_i / sum n.
    Ported from: la_tables.py:class_filer_weight ('effective filers'; unrounded here)
    Used in: la_class_filer_weight, la_class_concentration_brief ('effective filers')
    """
    cnt = pd.Series(counts, dtype=float)
    p = cnt / cnt.sum()
    return 1.0 / float((p ** 2).sum())


def top_k_share(labels: pd.Series, k: int) -> float:
    """Cumulative share of the k most common non-null labels (NaN if none).

    Formula: sum of the k largest s_i.
    Ported from: metrics.py:top_k_share
    """
    p = labels.dropna().value_counts(normalize=True)
    return float(p.head(k).sum()) if len(p) else float("nan")


def concentration(labels: pd.Series, top_n: int = 10) -> Dict[str, object]:
    """Distinct filers, singletons, top-n share, HHI, and the largest filer with its count (unrounded).

    Formula: counts = value_counts of non-null labels; singletons = #(count == 1);
             top_n_share = sum of the top_n counts / total; HHI = sum (count/total)^2.
    Defaults: top_n = 10. The archive rounded top_n share to 2 and HHI to 3 and joined
    largest and count into one string; here they are separate. total == 0: share is NaN.
    Ported from: metrics.py:concentration
    Used in: a2_d8_concentration
    """
    counts = labels.dropna().value_counts()
    total = int(counts.sum())
    return {"distinct": int(len(counts)),
            "singletons": int((counts == 1).sum()),
            "top_n_share": float(counts.head(top_n).sum() / total) if total else float("nan"),
            "hhi": hhi(labels),
            "largest": (counts.index[0] if len(counts) else ""),
            "largest_count": (int(counts.iloc[0]) if len(counts) else 0)}


def hhi_over_total(counts: pd.Series, total: int) -> float:
    """HHI of a subset of filers whose shares are taken over ALL ``total`` items (not over the subset).

    Formula: HHI = sum_i (n_i / total)^2 over the subset's counts n_i.
    Used for the named-company column of the document, where the denominator is every analysis patent.
    Ported from: a2.py:d8_concentration (cc_stats["hhi"], before rounding)
    Used in: a2_d8_concentration ('HHI', canonical-company column)
    """
    return float(((counts / total) ** 2).sum())


def top_n_share_over_total(counts: pd.Series, total: int, top_n: int = 10) -> float:
    """Share of ALL ``total`` items held by the ``top_n`` largest filers of a subset.

    Formula: sum of the top_n counts / total.
    Ported from: a2.py:d8_concentration (cc_stats["top10_share"], before rounding)
    Used in: a2_d8_concentration ('Top-10 share', canonical-company column)
    """
    return float(counts.head(top_n).sum() / total)


def coverage_segments(sizes: pd.Series, total: int, cuts: Sequence[int] = (10, 5, 2, 1)) -> pd.DataFrame:
    """Firm-size ranking cut into disjoint bands: firms and aircraft per band, with cumulative counts.

    Formula: band k = firms whose aircraft count s satisfies lo <= s < hi (first band has no hi);
             firms = #firms, aircraft = sum s, share = aircraft / total,
             cumulative firms / aircraft = those with s >= lo. Empty bands are omitted.
    Defaults: cuts = [10, 5, 2, 1] (lo bounds; each band's hi is the previous lo). ``sizes`` is
    aircraft per firm; ``total`` the analysis-set size. Columns: lo, hi (NaN for the open band),
    firms, aircraft, share, cumulative_firms, cumulative_aircraft.
    Ported from: la_tables.py:coverage_segments (numeric part)
    Used in: la_coverage_segments
    """
    cuts = list(cuts)
    rows = []
    for hi, lo in zip([None] + cuts[:-1], cuts):
        sel = sizes[(sizes >= lo) & ((sizes < hi) if hi else True)]
        if not len(sel):
            continue
        rows.append({"lo": lo, "hi": (np.nan if hi is None else hi),
                     "firms": int(len(sel)), "aircraft": int(sel.sum()),
                     "share": float(sel.sum() / total),
                     "cumulative_firms": int((sizes >= lo).sum()),
                     "cumulative_aircraft": int(sizes[sizes >= lo].sum())})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------- firm leverage
def share_shift_when_dropped(classes: pd.Series, firm_key: pd.Series, firm,
                             base_index: Optional[pd.Index] = None) -> pd.Series:
    """Change of every class's share when one firm's aircraft are removed (fractions; + = share rises).

    Formula: shift_c = share_c(without firm) - share_c(all), shares over non-null ``classes`` and
             read on the classes of the full set (``base_index``, default the classes of ``classes``
             in value_counts order); a class absent without the firm counts as 0.
    ``firm_key`` is the column the firm is dropped on (rows with NaN key are KEPT, as the archive's
    ~eq()); ``classes`` and ``firm_key`` share an index.
    Ported from: la_tables.py:firm_leverage (loop body) and sm_open.py:firm_leverage_classes
    Used in: la_firm_leverage, la_firm_leverage_classes
    """
    base = classes.value_counts(normalize=True)
    idx = base.index if base_index is None else base_index
    base = base.reindex(idx).fillna(0) if base_index is not None else base
    kept = classes[~firm_key.eq(firm)]
    return kept.value_counts(normalize=True).reindex(idx).fillna(0) - base


def firm_leverage(classes: pd.Series, firm_key: pd.Series, candidates: Sequence,
                  window: Optional[pd.Series] = None, windows: Sequence = (),
                  min_window_n: int = 30) -> pd.DataFrame:
    """For each candidate firm, the largest class-share move when it is dropped (whole set and per window).

    Formula: d_c = share_c(without firm) - share_c(all); class_moved = argmax_c |d_c|; shift = d at that
             class (signed, fraction). Inside each window in ``windows`` holding at least
             ``min_window_n`` (30) aircraft AND at least one aircraft of the firm, the same
             computation on the window; the window with the largest |d| (strictly greater, first
             wins ties) gives window_shift (fraction, unsigned), window, window_class.
    ``candidates`` is the firm list (the archive: firms with >= 3 aircraft, from firm_sizes);
    ``firm_key`` the column the firm is dropped on. NOTE the archive ranks sizes on ``firm`` but drops
    on ``company_canonical``; pass what the document passed. ``windows`` = WINDOW_NAMES[:-1] (all but
    the partial last window). Output order follows ``candidates``; the archive then sorts by
    |shift| descending.
    Ported from: la_tables.py:firm_leverage
    Used in: la_firm_leverage
    """
    base_all = classes.value_counts(normalize=True)
    rows = []
    for f in candidates:
        d = (classes[~firm_key.eq(f)].value_counts(normalize=True).reindex(base_all.index).fillna(0)
             - base_all)
        moved = d.abs().idxmax()
        worst_w, worst_pp, worst_c = "", 0.0, ""
        if window is not None:
            for wn in windows:
                m = window.eq(wn)
                sub = classes[m]
                fk = firm_key[m]
                if len(sub) < min_window_n or not fk.eq(f).any():
                    continue
                b = sub.value_counts(normalize=True)
                dw = sub[~fk.eq(f)].value_counts(normalize=True).reindex(b.index).fillna(0) - b
                if float(dw.abs().max()) > worst_pp:
                    worst_w, worst_pp, worst_c = wn, float(dw.abs().max()), dw.abs().idxmax()
        rows.append({"firm": f, "class_moved": moved, "shift": float(d[moved]),
                     "window_shift": worst_pp, "window": worst_w, "window_class": worst_c})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------- class concentration
def class_concentration(classes: pd.Series, firm: pd.Series, named: pd.Series) -> pd.DataFrame:
    """Per class: named firms filing in it, the largest and the top three, and the share held by named firms.

    Formula: n_c = aircraft of class c; named = value_counts of ``firm`` over the class's named
             aircraft; largest_share = named[0] / n_c; top3_share = sum(named[:3]) / n_c;
             named_share = sum(named) / n_c. Classes in value_counts order (non-null classes).
             Largest-share and top-3 are 0.0 when no named firm files in the class.
    Ported from: la_tables.py:class_concentration
    Used in: la_class_concentration (printed to 2 decimals)
    """
    tot = classes.value_counts()
    rows = []
    for c, n in tot.items():
        nm = firm[classes.eq(c) & named.astype(bool)].value_counts()
        rows.append({"class": c, "aircraft": int(n), "named_firms": int(len(nm)),
                     "largest_firm": (nm.index[0] if len(nm) else ""),
                     "largest_share": float(nm.iloc[0] / n) if len(nm) else 0.0,
                     "top3_share": float(nm.head(3).sum() / n) if len(nm) else 0.0,
                     "named_share": float(nm.sum() / n) if len(nm) else 0.0})
    return pd.DataFrame(rows)


def class_filer_concentration(classes: pd.Series, filers: pd.Series) -> pd.DataFrame:
    """Per class: distinct filers, the largest filer, its share, the top three's share, effective filers.

    Formula: cnt = aircraft per filer inside the class; its_share = cnt[0]/n_c;
             top3_share = sum(cnt[:3])/n_c; effective_filers = 1 / sum (cnt/sum cnt)^2.
    Classes taken over non-null ``classes`` (groupby order); sorting and rounding left to the caller.
    Ported from: la_tables.py:class_filer_weight (concentration columns)
    Used in: la_class_filer_weight, la_class_concentration_brief
    """
    rows = []
    d = pd.DataFrame({"c": classes, "f": filers}).dropna(subset=["c"])
    for c, sub in d.groupby("c"):
        cnt = sub["f"].value_counts()
        p = cnt / cnt.sum()
        rows.append({"class": c, "aircraft": int(len(sub)), "filers": int(cnt.size),
                     "largest_filer": cnt.index[0], "its_aircraft": int(cnt.iloc[0]),
                     "its_share": float(cnt.iloc[0] / len(sub)),
                     "top3_share": float(cnt.head(3).sum() / len(sub)),
                     "effective_filers": 1.0 / float((p ** 2).sum())})
    return pd.DataFrame(rows)


def top_filer_share(filers: pd.Series) -> Dict[str, object]:
    """Largest filer of a set of aircraft: who, its aircraft, how many filers, its share.

    Formula: share = max count / n aircraft.
    Ported from: la_tables.py:class_window_filer_weight (per class x window cell; min_n cut left to the caller)
    Used in: la_class_window_filer_weight
    """
    cnt = filers.value_counts()
    return {"largest_filer": cnt.index[0], "its_aircraft": int(cnt.iloc[0]),
            "filers": int(cnt.size), "aircraft": int(len(filers)),
            "its_share": float(cnt.iloc[0] / len(filers))}


# --------------------------------------------------------------------- one vote per filer
def vote_shares_modal(classes: pd.Series, filers: pd.Series) -> pd.Series:
    """Class shares when every filer votes once for the class it holds most of (value_counts order breaks ties).

    Formula: vote_f = argmax_c n_{f,c} (first in value_counts order on a tie);
             share_c = #filers voting c / #filers.
    ``classes`` / ``filers`` are already restricted to the rows to count (non-null class), e.g. one window.
    Ported from: la_tables.py:firm_weighted_shares
    Used in: la_firm_weighted_shares ('share by filer')
    """
    votes = (pd.DataFrame({"f": filers, "c": classes}).groupby("f")["c"]
             .agg(lambda s: s.value_counts().index[0]))
    return votes.value_counts(normalize=True)


def vote_counts_size_tiebreak(classes: pd.Series, filers: pd.Series) -> pd.Series:
    """Votes per class when every filer votes once for its most frequent class, ties broken on the class's own size.

    Formula: vote_f = argmax_c n_{f,c}; on a tie the class that is larger over the whole set wins
             (candidate classes sorted by decreasing overall size before idxmax); returns #filers per class.
    ``classes`` / ``filers`` are the non-null-class rows. Share = votes / votes.sum().
    Ported from: la_tables.py:class_filer_weight (the ``vote`` / ``votes`` variables)
    Used in: la_class_filer_weight ('share one vote per filer', 'repetition factor' = share by aircraft / this)
    """
    size = classes.value_counts()
    d = pd.DataFrame({"f": filers, "c": classes})
    vote = (d.groupby("f")["c"]
            .agg(lambda s: s.value_counts().sort_values(ascending=False)
                 .reindex(sorted(set(s), key=lambda c: -size.get(c, 0)), fill_value=0).idxmax()))
    return vote.value_counts()
