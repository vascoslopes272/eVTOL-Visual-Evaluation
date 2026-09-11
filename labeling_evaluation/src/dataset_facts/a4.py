"""A.4 — architecture from the text: the reading pass of 2026-09-09 and its confirmation.

All 695 approved primary patents were read from text only (title, abstract,
claim 1 and the description sentences that mention tilting, fixed units, lift,
cruise, wings, stopping or folding) and assigned one of the 11 wizard
architecture types or "not stated", with a quote and a confidence. The figures
were never opened, so this is an independent second reading, and the agreement
with the image labels is a validity check between modalities — not a reliability
coefficient, and not a ground truth. The ground truth is the citation, confirmed
by the annotator.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from . import metrics
from .loaders import Dataset

#: the text reading's code for "the patent does not state an architecture"
NOT_STATED = "NS"
#: how a multi-architecture patent's image label is written in the reading file
MULTI_SEP = "|"
CONFIDENCE_NAMES = {"H": "high", "M": "medium", "L": "low"}


def _reading(ds: Dataset) -> pd.DataFrame:
    if ds.text_arch is None:
        raise FileNotFoundError(
            "text_architecture/architecture_text_Claude_20260909.csv is missing"
        )
    t = ds.text_arch.copy()
    t["is_multi"] = t["image_label"].astype(str).str.contains(
        MULTI_SEP, regex=False
    )
    t["states_a_type"] = t["text_label"].ne(NOT_STATED)
    return t


def what_was_done(ds: Dataset) -> pd.DataFrame:
    """How many patents were read, and how many state an architecture at all."""
    t = _reading(ds)
    rows = [
        ("Approved primary patents read from text only", int(len(t))),
        ("Patents whose text states an architecture", int(t["states_a_type"].sum())),
        ("Patents whose text does not (component patents, control methods, "
         "design patents)", int((~t["states_a_type"]).sum())),
        ("Patents drawing a single architecture", int((~t["is_multi"]).sum())),
        ("Patents drawing more than one architecture", int(t["is_multi"].sum())),
    ]
    return pd.DataFrame(rows, columns=["the reading pass", "patents"])


def agreement_with_images(ds: Dataset) -> Dict:
    """Agreement and kappa on the single-type patents whose text states a type.

    This is the comparison the document reports: 68.1 % raw, kappa 0.61, against
    25.7 % and kappa 0.13 for the SBERT/keyword guess it replaces (A.1).
    """
    t = _reading(ds)
    single = t[~t["is_multi"] & t["states_a_type"]]
    out = dict(metrics.agreement(single["image_label"], single["text_label"]))
    # the quick-override records carry no image label, so they form no pair
    out["single_type_patents_stating_a_type"] = int(len(single))
    out["without_an_image_label"] = int(single["image_label"].isna().sum())
    for code, name in CONFIDENCE_NAMES.items():
        sub = single[single["confidence"] == code]
        out[f"{name}_n"] = int(len(sub))
        out[f"{name}_agreement"] = (
            round(float((sub["image_label"] == sub["text_label"]).mean()), 2)
            if len(sub) else float("nan")
        )
    multi = t[t["is_multi"] & t["states_a_type"]]
    among = [
        row.text_label in set(str(row.image_label).split(MULTI_SEP))
        for row in multi.itertuples()
    ]
    out["multi_type_patents"] = int(len(multi))
    out["text_type_is_among_the_drawn"] = round(float(np.mean(among)), 2) if among else float("nan")
    return out


def agreement_by_type(ds: Dataset) -> pd.DataFrame:
    """Share of each image class that the text recovers."""
    t = _reading(ds)
    single = t[~t["is_multi"] & t["states_a_type"]]
    hit = single["image_label"].eq(single["text_label"])
    g = pd.DataFrame({
        "aircraft": single.groupby("image_label").size(),
        "recovered": hit.groupby(single["image_label"]).mean().round(2),
    })
    g.insert(0, "name", [metrics.ARCH_NAMES.get(k, k) for k in g.index])
    return g.sort_values("recovered", ascending=False).reset_index(
        names="image_label"
    )


def disagreements(ds: Dataset, min_count: int = 4) -> pd.DataFrame:
    """The confusion pairs, which are not random.

    Each is a case where the claim states *that* propulsors tilt but not whether
    all of them do, or where the distinguishing fact is visual.
    """
    t = _reading(ds)
    single = t[~t["is_multi"] & t["states_a_type"]]
    wrong = single[single["image_label"] != single["text_label"]]
    pairs = wrong.groupby(["image_label", "text_label"]).size().reset_index(name="patents")
    pairs = pairs[pairs["patents"] >= min_count]
    pairs.insert(0, "image reads", pairs["image_label"].map(metrics.ARCH_NAMES))
    pairs.insert(1, "text reads", pairs["text_label"].map(metrics.ARCH_NAMES))
    return pairs.sort_values("patents", ascending=False).reset_index(drop=True)


def confusion_matrix(ds: Dataset) -> pd.DataFrame:
    """The full image-versus-text table that feeds RQ4."""
    t = _reading(ds)
    single = t[~t["is_multi"] & t["states_a_type"]]
    return pd.crosstab(single["image_label"], single["text_label"])


# --------------------------------------------------------------------------
# the confirmation protocol
# --------------------------------------------------------------------------
def confirmation_protocol(ds: Dataset) -> pd.DataFrame:
    """What each patent needs before its architecture is defensible.

    The rule: everything that rests only on a text reading needs the patent's own
    words, confirmed; a patent whose depicted aircraft is a known model with a
    public architecture needs nothing.
    """
    t = _reading(ds)
    final = ds.text_arch_final
    exempt = set()
    if final is not None:
        exempt = set(final.loc[final["provenance"] == "known_aircraft", "patent_id"])

    t = t[~t["patent_id"].isin(exempt)]
    agree = (~t["is_multi"]) & t["states_a_type"] & t["image_label"].eq(t["text_label"])
    among = pd.Series(
        [row.text_label in set(str(row.image_label).split(MULTI_SEP))
         for row in t.itertuples()],
        index=t.index,
    )
    multi_agree = t["is_multi"] & t["states_a_type"] & among
    low = t["confidence"].eq("L")
    rows = [
        ("three independent sources agree: the figure label, the text reading "
         "(or its silence) and the published architecture of a documented "
         "aircraft of that assignee", len(exempt),
         "cleared automatically, provenance known_aircraft"),
        ("text and image agree, citation shown",
         int(((agree | multi_agree) & ~low).sum()),
         "the annotator reads the citation and confirms the type"),
        ("agree, but the text reading was low-confidence",
         int(((agree | multi_agree) & low).sum()), "same, read more carefully"),
        ("text != image",
         int((t["states_a_type"] & ~(agree | multi_agree)).sum()),
         "the annotator adjudicates"),
        ("text does not state an architecture; no citation exists",
         int((~t["states_a_type"]).sum()),
         "no decision; the image label stands with provenance not_stated"),
    ]
    out = pd.DataFrame(rows, columns=["what they are", "rows", "what happens"])
    out.attrs["screen_work"] = int(out.loc[1:3, "rows"].sum())
    out.attrs["read_and_confirm"] = int(out.loc[1:2, "rows"].sum())
    return out


def citation_quality(ds: Dataset) -> pd.DataFrame:
    """Every citation checked against the patent text mechanically."""
    if ds.quote_check is None:
        raise FileNotFoundError("text_architecture/quote_check.csv is missing")
    q = ds.quote_check
    check = metrics.share_table(q["quote_check"]).rename(columns={"value": "verbatim check"})
    section = metrics.share_table(q["quote_section"]).rename(columns={"value": "section"})
    check["kind"] = "verbatim check"
    section["kind"] = "section the citation comes from"
    check = check.rename(columns={"verbatim check": "value"})
    section = section.rename(columns={"section": "value"})
    # a citation drawn from more than one section is reported as "mixed"
    compound = section["value"].astype(str).str.contains("/")
    mixed = pd.DataFrame([{
        "kind": "section the citation comes from", "value": "mixed",
        "count": int(section.loc[compound, "count"].sum()),
        "share": round(float(section.loc[compound, "share"].sum()), 2),
    }])
    section = section[~compound]
    return pd.concat([check, section, mixed], ignore_index=True)[
        ["kind", "value", "count", "share"]
    ]


def known_aircraft_list(ds: Dataset) -> pd.DataFrame:
    """The gazetteer of documented aircraft, and which companies it cannot decide.

    The gazetteer attributes an aircraft by assignee and, where a company has
    several documented aircraft, chooses between them by filing year. That is a
    guess, harmless where all of a company's aircraft share one architecture and
    unsafe where they do not, so a company whose documented aircraft differ in
    architecture is excluded from the automatic exemption.
    """
    known = ds.known_aircraft
    if known is None:
        raise FileNotFoundError("known_aircraft_architecture.csv is missing")
    known = known.assign(known_type=known["known_type"].fillna("(unknown)").astype(str))
    g = known.groupby("company").agg(
        models=("aircraft_name", "size"),
        aircraft=("aircraft_name", lambda s: " · ".join(s.astype(str))),
        types=("known_type", lambda s: " · ".join(sorted(set(s)))),
    )
    g["architectures differ"] = known.groupby("company")["known_type"].nunique() > 1
    return g.sort_values(["architectures differ", "models"], ascending=False).reset_index()


# --------------------------------------------------------------------------
# patents that draw more than one aircraft
# --------------------------------------------------------------------------
def multi_aircraft_patents(ds: Dataset) -> pd.DataFrame:
    """How the two sides meet when a patent draws several aircraft.

    The image side holds one architecture per aircraft; the text side holds one
    per patent, because a patent has one text.
    """
    per_patent = ds.variants.groupby("patent_id")["topType"].agg(
        lambda s: set(s.dropna())
    )
    several = per_patent[ds.variants.groupby("patent_id").size() > 1]
    same = several[several.apply(len) == 1]
    differ = several[several.apply(len) > 1]

    t = _reading(ds).set_index("patent_id")
    among, none = 0, 0
    for pid, types in differ.items():
        label = t["text_label"].get(pid)
        if label is None or label == NOT_STATED:
            continue
        if label in types:
            among += 1
        else:
            none += 1
    rows = [
        ("Several aircraft, all of the same architecture", int(len(same)),
         "treated as a single-type patent; the text label is compared with that type"),
        ("Several aircraft of genuinely different architectures", int(len(differ)),
         f"the text type is among the patent's image types ({among} of {len(differ)}), "
         f"or none of them ({none})"),
    ]
    out = pd.DataFrame(rows, columns=["case", "patents", "how the comparison is made"])
    out.attrs["patents_with_several_aircraft"] = int(len(several))
    out.attrs["variants_they_contribute"] = int(
        ds.variants[ds.variants["patent_id"].isin(several.index)].shape[0]
    )
    return out


def final_state(ds: Dataset) -> pd.DataFrame:
    """Where the confirmation stands: provenance counts in architecture_text_final.csv."""
    if ds.text_arch_final is None:
        raise FileNotFoundError("architecture_text_final.csv is missing")
    return metrics.share_table(ds.text_arch_final["provenance"])
