# How to read this pack

2026-09-30. This pack holds everything produced so far for the DINOv2 chapter ("Visual Learning:
DINOv2 embeddings of patent drawings and photographs"), in one file to read and comment. It is
not one of the two final documents (the analysis of at most 20 pages and the advisor summary).
Those are built from this material after the review.

## The one decision this review serves

**Which frozen model carries the chapter: DINOv2 (base) or DINOv2 with registers?** Every other
question is closed. The two models were run on the same images with the same protocol; only
the model differs.

| score (kNN-5, maker held out, layer 24 CLS) | base | registers |
|---|---|---|
| patent drawings, 12 G1 classes | 0.178 | 0.235 |
| patent drawings, 5 parent classes | 0.333 | 0.445 |
| photos, 5 classes | 0.534 | 0.563 |
| patent to photo matching, right aircraft in top 10 / top 50 | 20 % / 37 % | 22 % / 48 % |

Against registers: once the view direction is removed (Part 3), the two models score the same.
The registers gain sits in the dominant directions the model shares with the drawing view.

## The Parts, in reading order

The short Parts come first; the four reports after them are the reference.

| Part | what it is | what to look at |
|---|---|---|
| 1 | the chapter plan: skeleton, every ruling, every test with its status | Section 2 (the chapter's sections) |
| 2 | registers test: attention collapse and scores, with the attention figure chosen for the chapter | the table in Section 1 and the figure |
| 3 | view erasure: does architecture survive removing the view? (yes) | the before/after table and the verdict |
| 4 | photo crop test: does the background carry the class signal? (no) | the numbers table and the montage at the end |
| 5, 6 | the patent-drawing analysis, base and registers | the Summary, and the comparison table right after it in Part 6 |
| 7, 8 | the photo analysis, base and registers | the Summary; Section 9 (matching) |
| 9 | links to the rotatable 3-D pages (base, registers, photos) | open next to Parts 5 and 6 |

Parts 5 and 6 (and 7 and 8) have identical structure: the same table number in both compares
the two models directly. Each report numbers its own figures and tables from 1.

## After reading

1. Say **base** or **registers**.
2. Comments: save a commented copy into `../comments/` (same routine as the Labelling Analysis
   brief). What to change in the analysis is applied there first; wording goes to the final
   documents.
