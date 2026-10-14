"""Question 4 text: do the patented aircraft stand for the aircraft that get built? (THESIS_CONTRACT.md §1, §2)

Numbers are placeholders resolved from viz.thesis_q4.numbers(ctx); nothing numeric is typed here.
"""

METHOD = """- **Objective:** Whether the drawing label matches the built aircraft, and whether publicly covered aircraft stand for the dataset.
- **Data and unit:** Unique aircraft; the {nc_named} named ones matched to evtol.news, the directory's class mix, NASA TRL per aircraft.
- **Procedure:** Pairwise agreement on matched aircraft, class mix against the directory, built and index-firm aircraft against the rest.
- **Test:** Wilson interval with finite-population correction; chi-square with adjusted residuals for two mixes; chi-square or Mann-Whitney per attribute.
- **Limit:** Matched aircraft are no random sample; TRL 2 is a floor; TRL and directory years are machine-read, unchecked."""

RESULTS = [
    dict(sub="A", title="Is the coding right", text="""The coding is checked first, on the matched aircraft, and the class mix second, against the evtol.news directory. The drawing label gives the built aircraft's architecture class for {pw_img_pub} of the {pw_n} matched aircraft ([tab:q4_coding_agreement]). That share, {pw_share}, has an interval of {pw_ci}. The patent text agrees with the public aircraft on {pw_txt_pub} of them, and the drawing agrees with the text on {pw_img_txt}. The disagreements are patents that describe another configuration than the one the firm built, and a few drawings read as one class when the text states another.

Only a named aircraft can be checked at all, {nc_named} of {unique}, so these shares speak for the company-backed part of the dataset. The rest was coded by the same reader with the same codebook."""),
    dict(sub="B", title="Is the mix representative", text="""Vectored Thrust is the largest class in every window of dataset and directory ([fig:q4_class_mix_dataset], [fig:q4_class_mix_directory]). Lift + Cruise rises in both, from {lc_ds_first} to {lc_ds_last} of the dataset's aircraft. In the directory it goes from {lc_dir_first} to {lc_dir_last}. All years together Wingless carries the gap between the two mixes (adjusted residual {resid_low}, [fig:q4_dataset_vs_directory_classes]). Restricting the directory to electric crewed pages leaves Wingless at {wm_domain}, so the domain gate does not explain the gap. Only the directory pages linked to a patent of this dataset match the dataset's mix (p {closest_p}, [fig:q4_dataset_vs_directory_subsets]).

[hl]The AAM Reality Index firms, the index firms, file before they fly ([fig:q4_patent_vs_market_clock]). {ff_before} of the {ff_flown} firms with a first flight on record filed their first patent in this corpus before flying.[/hl] [hl]The lead is a median of {ff_lead} years, and planned entry into service sits a median of {eis_lead} years after the first patent.[/hl]

[hl]Of the {unique} designs, {flown_n} have flown. They differ from the rest on {flown_differs} of the six attributes ([tab:q4_flown_representativeness]).[/hl] [hl]The {fari_n} designs of the index firms that have flown differ on {fari_differs} of the six ([tab:q4_flown_index_firm_representativeness]).[/hl] By architecture group the flown designs give p {flown_class_p}, the flown index-firm designs p {fari_class_p}.

The Wingless gap sits in the directory pages no patent of this corpus describes, so it rests on which aircraft get patented. The directory's Vectored Thrust pools Tilt Propulsor with CVT and Tilt Wing, so the Tilt Propulsor crossover of Q6 has no outside check. Whether the money follows is read next, in Q5."""),
]

ANSWER = """Where an aircraft can be checked, the drawing label gives the built aircraft's class {pw_share} of the time, on {pw_n} named aircraft. The class mix of the patented aircraft follows the directory's in Vectored Thrust and in the rise of Lift + Cruise, and parts from it most in Wingless (adjusted residual {resid_low}), a gap the domain gate does not explain. [hl]The index firms file a median of {ff_lead} years before their first flight, so a design is public before it flies.[/hl] [hl]The aircraft public sources cover, the {trl_n} that got built and the {ari_n} of the index firms, are company-backed and carry more propulsor units, so they do not stand for the dataset.[/hl] Neither group differs from the rest in architecture class, which is the one attribute the comparison with the built sector needs."""

APPENDIX = {
    "q4_dataset_vs_directory_classes": "All years together the two mixes differ (chi-square p {mix_p}), and Wingless carries the gap with an adjusted residual of {resid_low}.",
    "q4_dataset_vs_directory_subsets": "The directory pages linked to a patent of this dataset are the one part whose mix matches it (p {closest_p}); Wingless stays at {wm_domain} even in the in-domain pages, so the domain filter does not close the gap.",
    "q4_trl_by_class": "Only {trl_share} of the aircraft, {trl_n}, got past the paper stage of NASA TRL, and they come from the classes patented most, Lift + Cruise and Tilt Propulsor.",
    "q4_name_coverage": "{nc_named} aircraft carry a real product name and {nc_gen} a generated identifier; none of the generated ones could be matched to a public aircraft.",
}
