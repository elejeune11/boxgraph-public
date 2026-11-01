# Audit of elosegui2014

Second reading, 2026-11-01, by claude-opus-5-5 against `corpus/2014_Elosegui-Artola.pdf` (pages 1-34).

## Checked, no change

- PDF pages 8-34 (SI): confirmed blank in this copy. Text files are empty, page images are 90-byte files, and
  the PDF itself renders blank pages 8-10, 20, 21. The first reader's scope (article only) stands.
- `kont_a5b1`, `kont_avb6`, `koff_a5b1`, `koff_avb6` (p. 3, Fig. 2a table): digits 7.724, 3.893, 0.4944, 15.06
  and the column headers "Kont (M-1 s-1 x 10^5)", "Koff (s-1 x 10^2)" match the page image. Units and
  exponents as entered agree with the header (read literally); the ambiguity stays in `q_koff_column_multiplier`.
- `kont_ratio_half`, `density_ratio_fivefold` (p. 2): "decreased by only half", "fivefold higher" match the page.
- `kon_fold_model`, `koff_fold_model`, `density_onset_a5b1_pred`, `density_onset_avb6_pred`,
  `traction_peak_avb6_measured` (p. 6): "fivefold", "threefold", "14 kPa", "29 kPa", "5 kPa" match the page image.
- `catch_bond_min_force` (p. 4): "about 30 pN" matches; attributed to ref. 12 (Kong 2009) as printed.
- `kon_eff_ratio` (p. 2): kon = kont · dint as printed; the ratio form is correct for it.
  `kont_ratio`, `koff_ratio` (p. 2): plain ratios of the table values; correct.
- `integrin_clutch_sim` (p. 3-6): `runnable: false` is justified, since the equations and parameters are only
  in the unreadable SI.
- `added.yaml` is empty. No run needs an input the paper does not state, so nothing is missing.
- No further printed numerical result from a runnable model was found to compare. Other claims are
  qualitative ("kon ... predicted to be higher", "kon had to increase even more than koff", Fig. 3b
  "kon1 > kon2, koff1 > koff2"), or come from the non-runnable clutch model.
- No transcription error found, so no datum or model was changed.

## Added

- `q_fig3a_dint_label` (p. 4, Fig. 3a): new `possible_error`. The PDF text layer labels kon1 = kont1·dint2,
  which disagrees with the caption (dint1, dint2) and with p. 2. The image resolution available does not confirm it.
- `q_fig3d_onset_vs_14kPa` (p. 4, Fig. 3d; p. 6): new `reading` disagreement. By eye, the Fig. 3d model onset
  sits near 10 kPa, not 14 kPa, so citing Fig. 3d for `density_onset_a5b1_pred` may not hold. Left as a question.

## Not done

- Figure readings (Fig. 2b would test "fivefold"; Fig. 3c-e and Fig. 4d-l): PDF rendering commands
  (`pdftoppm`, `boxgraph figure page`) were refused in this audit session as well, as they were for the first reader.
