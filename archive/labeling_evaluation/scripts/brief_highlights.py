"""The key takeaways the Word REVIEW COPY of the brief colours — author's request, 2026-09-25.

Read by ``export_brief_docx.py`` when it exports ``LABELLING_ANALYSIS_BRIEF.md``. Colour is for
the author's review copy only: the PDF keeps the monochrome house style, and the findings
digest (for the advisors) is exported without it.

Each entry is a phrase that occurs in exactly the paragraph to colour, written as it reads in
the rendered text (no markdown ``**``). The exporter reports any phrase that matched nothing, so
a rewording of the brief shows up as a warning at export rather than as a silently lost colour.

How a matched paragraph is coloured: a short one (a bullet, a takeaway) whole; a long one only
in its bold runs — the author's rule is that bold marks importance, so in a long paragraph the
bold statement IS the takeaway, and colouring ten lines would highlight nothing.
"""

#: light fills a highlighter would give; readable in print and on screen
GREEN_FILL = "C6EFCE"
RED_FILL = "FFC7CE"

#: a paragraph longer than this is coloured in its bold runs only
WHOLE_PARAGRAPH_MAX = 600

#: GREEN — the findings. The comment numbers are the author's 2026-09-24 review, where he marked
#: the passage important; the rest are the chapter answers' core claims.
GREEN = [
    "Money goes with filing early, not with filing more.",           # 2026-09-26, ch4
    "No class converges on one layout",                                # 2026-09-26, 3.3
    "What moves inside the classes is one move toward more propulsors",    # 2026-09-26, 3.4
    "Where an aircraft can be checked, the drawing gives",            # 2026-09-26: chapter-1 answer
    "The aircraft that public sources cover do not stand for the record.",  # 2026-09-26
    # 2026-09-26 (chapter-3 review): the old dominant-design verdict ("No dominant design …",
    # "Not even read as one family", "One family, tested …") is overturned; see RED
    "Lift + Cruise has overtaken Tilt Propulsor.",                        # chapter-3 answer, 3.1
    "Closed at the class, open below it.",                            # the discovery curve
    "One destination.",                            # the chapter-4 answer
]

#: RED — results that OVERTURNED what an earlier version of this document said.
RED = [
    "The class mix moves with the whole population of filers.",       # was "arrival, not conversion, moves the mix"
    "eVTOL patenting grows faster than patenting at large",             # was "about twice as fast", then "as fast as aeronautics"
    "A design becomes public about",                                    # was 9 of 12 / 5 y (a planned flight counted)
    "have no patent left in force.",                                    # was "the classes lapse at the same rate"
    # 2026-09-26 (chapter-3 review, C53/C54): was "no dominant design at any level, in any
    # window"; per priority year on the aircraft in force the family F meets all three
    "eVTOL has a dominant design, but it is not one of the classes",    # chapter-3 answer lead
    "Only the family F meets the three conditions in the same period",  # la_dd_levels takeaway
]

LEGEND = ("Review copy. Green marks the key findings; red marks a result that overturned what an "
          "earlier version of this document said. The PDF and the findings digest carry no colour.")
