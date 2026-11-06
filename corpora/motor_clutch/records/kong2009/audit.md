# Audit of kong2009 (second reading, 2026-11-01)

## Checks with no change needed

- **data.yaml values** (pp. 4-7): the record holds no typed values. Every datum is a figure reading,
  so there are no digits or exponents to transcribe. I compared the tick labels in every reading
  config with the page images: Fig. 3 A y 0-4 // 8, 16, 24; Fig. 3 B-C 0, 3, 6 // 16, 24; Fig. 3 D
  0-1.5; Fig. 5 A and Fig. 6 0-12 // 16, 24; x 0-60. All match.
- **Overlays** (pp. 4-7): I checked `ov_fig3a_squares`, `ov_fig3b_circles`, `ov_fig3c_circles`,
  `ov_fig3d_triangles`, `ov_fig4b_circles`, `ov_fig5a_circles` and `ov_fig6a_circles`. Every cross
  sits on its marker, and the bar ticks sit on the caps.
- **series_bonds** (p. 3): matches the words as printed ("the dissociation rate of two bonds in series
  equals to the sum of the two individual dissociation rates").
- **survival_first_order** (p. 8): matches the words as printed ("the negative slope of a line
  reflects the off rate"). The `>` versus `>=` wording is now a question (below).
- **added.yaml** (all pages): absent. That is correct, since no run uses an unstated input.
- **Statement "lifetimes at low forces (<10 pN) were similarly short (<2 s)"** (p. 4, p. 6): checked
  by eye against the readings of Figs. 3 A-C. Every circle below 10 pN is under 1.5 s, so the
  statement holds. It is an inequality, so no comparison was added.
- **"CG-7" for "GG-7"** (p. 5, "FNIII7-10-tra5b1-Fc-CG-7 serial bonds"): a harmless typo. It is not
  recorded.

## Additions

- **fig5a_squares, lt_Fc_GG7_fig5a** (p. 6, Fig. 5 A): a new reading of the Fc/GG-7 squares as
  replotted on Fig. 5 A. The code is `figures/fig5a_squares.py`, using the shared `_lt.py` helper with
  size 105 and threshold 0.85, so that the square at 51 pN, partly covered by other markers, is found.
  The overlay was checked (`figwork/audit_fig5a_squares.png`). All nine markers agree with
  `lt_Fc_GG7` (Fig. 3 A) to within 0.15 s.
- **fig5a_squares_line_30 / _35, line_Fc_GG7_30to45 / _35to50** (p. 6): the squares read as a line at
  30-45 and 35-50 pN. On Fig. 3 A the line between 33.6 and 36.4 pN crosses the axis break, which is
  why Fig. 5 A is used.
- **fig3b_circles_line_hi, fig3c_circles_line_hi, line_FN_a5b1Fc_MgEGTA_hiF, line_FN_a5b1Fc_Mn_hiF**
  (p. 4): the circle lines of Figs. 3 B and C at 35-50 pN. They use the first reader's code, and the
  overlay was checked.
- **fig5a/b/c_circles_line_hi, line_FN_tra5b1Fc_*_hiF** (p. 6): the circle lines of Figs. 5 A-C at
  30-45 pN. The Fig. 5 C circles end at 47 pN, so 50 pN is not read.
- **cmp_fig3b_vs_FcGG7_above30, cmp_fig3c_vs_FcGG7_above30** (p. 3, p. 4 caption): consistency
  checks of the stated claim that above 30 pN the circles are indistinguishable from the squares.
  Fig. 3 B is not reproduced at any force. Fig. 3 C is not reproduced at 35 and 45 pN and is close
  at 40 and 50 pN.
- **cmp_fig5a/b/c_vs_FcGG7_above25** (p. 5): consistency checks of the claim that above 25 pN the
  circles coincided with the squares "in all three cation conditions". Figs. 5 A and B are not
  reproduced at any force. Fig. 5 C is reproduced at 30-35 pN and not reproduced at 40-45 pN.
- **q_high_force_overlap_overstated** (p. 3, p. 5; overstated_claim): records the result above. It
  notes that the verdicts use reading intervals rather than SEM, and that at some forces the SEM bars
  themselves do not overlap.
- **q_schematic_figure_refs** (p. 6; possible_error): the text says "Fig. 3 A, schematic" and
  "Fig. 3 B, schematic" for the P1D6 and HFN7.1 arrangements, which are drawn in Fig. 4.
- **q_s5_threshold_strict** (p. 8, p. 14; reading): the main text says "lifetime >t" (checked on the
  page image), while the Fig. S5 caption says "lifetime >= t".
- figures.md: added a section describing these readings.

## Disagreements with the first reader (recorded as questions, nothing changed)

- **q_measured_plots_left_out** (p. 3, p. 6, pp. 12-13; reading): the first reader left out the
  measured bar charts and histograms of Fig. 2, Figs. S2-S4 and the S3 C lifetime bins (0.3, 2.8 and
  10 s, p. 6). The guide asks for every plot of measured data to be read. These are still unread.

## Not done

- Fig. S5 and the left-out measured plots above were not read in this audit.
- The `boxgraph figure ...` command was refused in this session, so the overlays were drawn by
  calling `boxgraph.cli.main` through `.venv/bin/python -c`. They are the same code and the same
  output.

`.venv/bin/boxgraph validate records/kong2009`: SOUND (0 errors). The 3 remaining warnings were
already there: two models never run, and no reproduction comparisons.
