# Audit of pries1992

Second, independent reading against the page images (pp. 1-9). Figures were not read.

## Checked, no change

- Table 2 (p. 3): every B and C entered in `C_table2_capillaries`, `B_table2_capillaries`,
  `C_table2_tubes`, `B_table2_tubes`, `C_table2_tubes_second`, `B_table2_tubes_second`,
  `C_20_185cP`, `B_20_185cP`, `C_20_55cP`, `B_20_55cP`, `C_20_9cP`, `B_20_9cP` and `D_20`
  matches the page image: digits, signs, trailing zeros and diameters. The split of the
  duplicate 811 um and 930 um rows matches the table's row order.
- `C_text_185cP`, `C_text_55cP`, `C_text_9cP` (p. 7): "-0." / "901", "-0.814", "-0.599" as printed.
- `C_assigned_capillaries` (p. 5), `eta045_large_tubes`, `eta045_minimum`, `D_minimum` (p. 4),
  `HctD_045` (p. 6), `HctT_fig6` (p. 7): as printed.
- Models `eq2_eta045` (Eq. 2, p. 5), `eq4_C` (Eq. 4, p. 6), `eq6_B_diameter` (Eqs. 5-6, p. 6),
  `eq7_eta_combined` (Eq. 7, p. 6), `eq8_tube_hct` (Eqs. 8-9, p. 7) and `eq10_discharge_hct`
  (Eq. 10, p. 7) match the printed equations: coefficients, signs, exponents. Eq. 10 is the
  correct algebraic solution of Eq. 8 for the '+' root. No transcription errors found.
- `added.yaml`: `D_large_tubes` and `D_fahraeus_check` have bases and real alternatives. No change.

## Changes

- Added `B_table2_brooks_rotational`, `C_table2_brooks_rotational`, `B_table2_chien_rotational`,
  `C_table2_chien_rotational` (p. 3): the two rotational-viscometer rows of Table 2, which were
  not entered. They carry no diameter, so no model is run on them.
- Added question `q_eq10_root_small_D` (p. 7): printed Eq. 10 gives Hct_D > 1 for D < ~3.06 um
  (X > 1), while Fig. 6 starts at 2 um. Checked by running `eq10_discharge_hct` directly
  (Hct_T = 0.45: Hct_D 4.5 at 2 um, 8.7 at 2.5 um, 80 at 3.0 um; 0.46 at 3.3 um).
- Added question `q_fig3_n_12um` (p. 5 vs p. 3): Fig. 3 labels the 12 um panel n:60, Table 2
  gives n = 54.
- Added question `q_fig5_caption_fig1` (p. 6): the Fig. 5 caption refers to "data given in
  Fig. 1", which is the viscometer drawing; Fig. 2 is meant.
- Added question `q_eq1_not_modelled` (p. 4, kind `reading`): Eq. 1 (extrapolation to
  Hct 0.45) is not a model in the record; no printed number rests on it until the Fig. 2
  points are read.

## Disagreements and remarks

- The validator warns that the record has no `reproduction` comparison. I agree with the first
  reader that none is possible from printed numbers alone: the paper's model outputs
  (the lines of Figs. 2-6) are only plotted. They wait for the figure job.
- `source.yaml` gives the reader's model as `None`; that is the first reader's metadata and was left as it is.
