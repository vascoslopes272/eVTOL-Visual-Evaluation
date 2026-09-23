# Dated sector events — the timeline strip of Figure 2.1.1

**This is the author's first pass (compiled 2026-09-23), meant to be edited.** Figure 2.1.1 of
the Labelling Analysis counts eVTOL filings per priority year; the author's ruling of 2026-09-23
is that the *overall rise* in patenting is read against what happened outside the patent record
(the Uber Elevate paper, first flights, certification rules, listings, insolvencies), and never
tested against morphology. Battery specific energy belongs to the same reading but is a trend,
not an event, so it is not a row here.

`src/dataset_facts/la_figures.fig_filings_per_year` **reads `sector_events.csv` at render time**:
edit the file, not the code. A missing or empty file draws the figure without the strip.

## Columns

| column | what goes in it |
|---|---|
| `date` | ISO date `YYYY-MM-DD` of the event (the calendar date, as the source states it) |
| `event` | the label printed on the figure — keep it to **28 characters**; longer labels are cut with `…` and a warning is printed. The strip is exactly as tall as the longest label (about 1.35 in at 28 characters, 7 pt), so shorter labels make a shorter figure |
| `source_url` | one citable source: the original document, the company's or the regulator's own page, or an SEC filing |
| `note` | what happened, in a sentence, with the secondary dates and links (the note is not printed) |

## How the figure places them

- The axis of Figure 2.1.1 is the **priority year** of the filings. An event dated by calendar
  date **stands on its year**: the Uber Elevate paper of 27 October 2016 stands on the 2016 bar,
  although most 2016 priority filings precede it. The How-to-read line under the figure says so.
- Two or more events in one year stand side by side, half a year apart, in date order.
- Events dated after the PatSeer snapshot (2026-06-08) are not drawn; events before 2005 would
  stand on the pooled ≤2005 bar. Both cases print a line when the figure is rendered.
- Keep the list to 8–12 rows: one axis, one label per event, readable in black and white.

## The twelve rows and how each date was checked (2026-09-23)

| date | event | checked against |
|---|---|---|
| 2011-10-21 | first crewed multicopter (e-volo/Volocopter VC1) | Vertical Flight Society directory page |
| 2016-10-27 | Uber Elevate white paper | the paper itself (VFS archive of the PDF); Uber's Medium post |
| 2017-04-25 | first Uber Elevate Summit, Dallas | Uber's summit page (place); TechCrunch 20 Apr 2017 (dates 25–27 Apr) |
| 2018-01-31 | Airbus Vahana Alpha One first flight | Airbus press release |
| 2019-05-04 | Lilium Jet five-seater first flight | Lilium press release (as carried by Vertical; lilium.com unreachable) |
| 2019-07-02 | EASA SC-VTOL-01 published | EASA document-library page |
| 2020-12-08 | Joby acquires Uber Elevate | Joby investor-relations release |
| 2021-08-11 | Joby / Lilium / Archer / Vertical public listings (dated by Joby's, the first) | Joby IR release; Nasdaq release (Lilium, 15 Sep); Archer IR (17 Sep); SEC 6-K (Vertical, 16 Dec) |
| 2023-10-13 | EHang EH216-S, world's first eVTOL type certificate (CAAC) | EHang news release |
| 2024-10-22 | FAA powered-lift final rule (Part 194 SFAR) | FAA newsroom (release 22 Oct); Federal Register 21 Nov 2024, 89 FR 92296; in force 21 Jan 2025 |
| 2024-10-28 | Lilium (28 Oct 2024) and Volocopter (26 Dec 2024) file for insolvency — one marker, dated by the first | Lilium SEC 6-K of 29 Oct 2024; Volocopter press release (Runway Girl Network copy); second Lilium filing 21 Feb 2025 (electrive) |
| 2025-03-30 | first commercial passenger eVTOL service (EHang operators, CAAC air operator certificates) | EHang news release |

Every date in the author's candidate list was confirmed; none was struck. Added to it: the
2011 VC1 flight (the sector's first crewed flight, five years before the rise), EHang's type
certificate (2023), Volocopter's insolvency (folded into the Lilium marker) and the first
commercial service (2025).

## Checked but not included (add a row if wanted)

- 2017-09-25 — Volocopter 2X, first public flight of an autonomous air taxi, Dubai (RTA):
  https://www.volocopter.com/en/newsroom/first-ever-public-demonstration-of-an-autonomous-urban-air-taxi
- 2017-04-20 — Lilium two-seat prototype first flight (superseded here by the five-seater of 2019)
- 2022-09-21 — Kitty Hawk (Larry Page) shuts down; Wisk continues:
  https://verticalmag.com/news/larry-pages-evtol-startup-kitty-hawk-winding-down-operations/
- 2025-03-10 — Wanfeng (Diamond Aircraft) buys Volocopter's assets (in the insolvency note)
- 2026-03 — Joby begins FAA Type Inspection Authorization flight testing, the last stage before a
  type certificate (https://www.jobyaviation.com/news/joby-s-first-faa-conforming-aircraft-takes-flight);
  no FAA type certificate and no Dubai passenger service before the 2026-06 snapshot.
- Joby's and Archer's UAE and US commercial launches: planned for 2026, not before the snapshot.
