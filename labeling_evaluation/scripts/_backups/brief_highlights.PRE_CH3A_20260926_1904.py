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
    "Where an aircraft can be checked, the drawing gives",            # 2026-09-26: chapter-1 answer
    "The aircraft that public sources cover do not stand for the record.",  # 2026-09-26
    "No dominant design, on any of the three conditions.",           # the chapter-2 verdict
    "Not even read as one family.",                                   # C36: the family test
    "One family, tested because the record suggested it",            # C36, "the thing of my thesis"
    "What moves is one move.",                                        # C37: "major importance"
    "Three of the four traces are one move",                          # C37 + C38: both "major importance"
    "The duct leaves CVT, because the airframe around it leaves.",    # C38: "major importance"
    "Closed at the class, open below it.",                            # the discovery curve
    "Arrival moves the mix, not conversion.",                         # C44: "also very important"
    "Entry dominates every window",                                   # C44, the takeaway itself
    "Tilt Wing is the exception and the diagnostic.",                 # C47: "this is an important thing"
    "should take the null as the finding",                            # the chapter-4 answer
]

#: RED — results that OVERTURNED what an earlier version of this document said.
RED = [
    "eVTOL patenting grows faster than patenting at large",             # was "about twice as fast", then "as fast as aeronautics"
    "A design becomes public about",                                    # was 9 of 12 / 5 y (a planned flight counted)
    "have no patent left in force.",                                    # was "the classes lapse at the same rate"
    "Per propulsive unit, tilting joints fall",                         # was "against both cost drivers"
    "Counted per propulsive unit they fall, so cost wins",              # the same correction, driver answer
    "That verdict does not survive normalisation",                      # the same correction, observation 1
]

LEGEND = ("Review copy. Green marks the key findings; red marks a result that overturned what an "
          "earlier version of this document said. The PDF and the findings digest carry no colour.")
