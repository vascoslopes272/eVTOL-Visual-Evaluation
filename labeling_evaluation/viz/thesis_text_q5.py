"""Q5 — Does the money follow the patents, in time and in design? Text of the thesis layer (see THESIS_CONTRACT.md).

Every number is a {placeholder} resolved from viz.thesis_q5.numbers(ctx). Markup: [fig:name] / [tab:name] place the item
after the paragraph that first cites it; [hl]…[/hl] marks the sentence that depends on a flagged item.
"""

METHOD = """- **Objective:** Whether the disclosed money follows the patent record, in time and in what it funds.
- **Data and unit:** The firm, {ari_firms_n} AAM Reality Index firms filing here, with funding, first flight, entry into service.
- **Procedure:** Years from first patent here to first flight, less the publication lag; two-firm funding share beside aircraft share.
- **Test:** Spearman ρ of funding against aircraft, first-patent year and lead; sector investment compared by eye.
- **Limit:** The lead is a floor; index firms differ from the corpus; only strong relations show on few firms."""

RESULTS = [
    dict(sub="A", title="Timing", text="""A design reaches the patent record years before it flies. Of the {ari_timeline_n} \
index firms that file here, {ff_record_n} have a first flight on record up to the release year. Of those, {ff_before_n} filed \
their first patent in this corpus before flying, a median of {ff_lead} years earlier. For the rest the first flight comes \
first, which only means that their earliest filing is not in this corpus. [hl]Planned entry into service sits a median of \
{eis_lead} years after the first patent on the {eis_n} firms that state one, firm by firm in [tab:q5_ari_timeline].[/hl]

The lead a reader of published patents can use is shorter, because a patent is published up to {lag_p90} years after its \
priority date and a priority year can only be read that many years later. Once that lag is paid, about {ff_visible} year of \
the median lead is left."""),
    dict(sub="B", title="Funding vs filing and output", text="""The better-funded firms do not hold detectably more aircraft. \
[fig:q5_funding_vs_aircraft] sets the disclosed funding of the firms with an amount against their unique aircraft in the \
corpus, ρ {rho_air} with p {p_air}, no relation detected. {best_firm}, the best funded, holds {best_air} aircraft. Money does \
go with filing early, ρ {rho_fp} against the priority year of the first patent with p {p_fp}, and the best-funded firm filed \
first. [hl]The lead from first patent to first flight does not shorten with money either, ρ {rho_lead} with p {p_lead} on the \
firms whose first flight has happened ([fig:q5_patent_lead_to_flight]).[/hl]

On so few firms that one relation, one of three tested, is a lead to follow."""),
    dict(sub="C", title="Concentration of funding", text="""The money is concentrated in {top1} and {top2}, where the patents \
are not. These two firms hold {top2_fundshare} of the funding the index firms disclose and {top2_airshare} of the aircraft of \
this labelled dataset. Knowing who has the money therefore says little about who files the designs, since the design space \
is filled by many small filers (Q2).

Disclosed eVTOL investment totalled about US$ {ext_fund_1020} billion over the whole decade to {ext_fund_1020_end} (Vertical \
Flight Society), after the filings had already climbed and held their level. The year {fund_peak_period} alone then brought about \
{ext_fund_2021} billion (McKinsey), so the sector's money came later than its patents. [hl][fig:q5_patenting_vs_investment] sets \
money per year against aircraft per year for each published period, where the {fund_peak_period} dot sits highest on both axes. \
The two trackers differ in scope, so the comparison is by eye.[/hl]"""),
]

ANSWER = """The money follows the patents in time, with the patent in front, since {ff_before_n} of the index firms with a flight \
on record filed before flying, a median of {ff_lead} years earlier. Sector investment multiplied only in {fund_peak_period}, after filings \
had held their level since {air_level_year}. The money does not follow the patents in output, since on the firms with a disclosed amount \
funding goes with no detectably larger number of aircraft (ρ {rho_air}, p {p_air}) and with no detectably shorter lead to first flight. \
The one relation detected is with filing early, ρ {rho_fp} against the priority year of the first patent with p {p_fp}. \
The money is also far more concentrated than the designs, {top2_fundshare} of the disclosed funding in two firms that hold \
{top2_airshare} of the aircraft."""

APPENDIX = {
    "q5_ari_timeline": "Of the index firms with a first flight on record, {ff_before_n} filed their first patent here before "
                       "flying, a median of {ff_lead} years earlier, and the lead is a floor.",
    "q5_patent_lead_to_flight": "Funding against the lead from first patent to first flight gives ρ {rho_lead} with p {p_lead}, "
                                "no relation detected on so few firms.",
    "q5_patenting_vs_investment": "Aircraft per priority year held their level from {air_level_year}, while disclosed investment per year "
                                  "multiplied only in {fund_peak_period}.",
}
