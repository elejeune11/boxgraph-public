# Audit: elosegui2016

Second, independent reading against `corpus/2016_Elosegui-Artola.pdf`. Date: 2026-11-01; auditor:
claude-opus-5-5.

## Values checked (no transcription errors found)

- `nf_table`, `kont_table`, `nm_table`, `dadd_table`, `FR_table`, `Fm_table`, `vu_table`, `dint_table`,
  `kc_table`, `ra_table` (p. 19, Supplementary Table 1): digits, exponent (2.11 x 10^-4) and units
  (um^2/s, /um^2, pN, nm/s, nN/nm, nm) match the page image.
- `S_nf_table` 1.66, `S_kont_table` 1.49, `S_nm_table` -1.16, `S_dadd_table` -0.83, `S_FR_table` -0.95
  (p. 19): signs and digits match.
- `dt_note` 5 ms, `t_total_note` 100 s (p. 23); `koff_scale_note` 0.9, `low_force_note` < 1 pN (p. 24);
  `threshold_increase_note` 10% (p. 25): match.
- `nf_fig6a/b/c` 750/1200/1650, `kont_fig6d/e/f` 1.9/1.5/0.9 x 10^-4 um^2/s, `dadd_fig6d/e/f` 24/10/6,
  `nm_fig6g/h/i` 500/300/180 (p. 7, Fig. 6 caption): match the page image, exponents included.
- `FR_text` 7.3% (p. 8), `threshold_measured_text` 5 kPa (p. 2), `talin_unfolding_force_wt` 5 pN and
  `talin_unfolding_force_ivvi` 8 pN (p. 5): match.
- `E_gel_4p71` 4.71 ± 0.22 kPa, `E_gel_29p45` 29.45 ± 0.10 kPa (p. 20, Supplementary Table 2): match.

## Models checked

- `clutch_talin_sim` (pp. 23-25): matches the note's words (kon = kont dint; catch-bond koff times 0.9;
  unfolding with FR f; unfolding must precede unbinding and fall in the step; vinculin kvin vs refolding
  kfold; +dadd on reinforcement, -dadd on unbinding, floor at basal dint; linear force-velocity from va to
  0 at nm Fm). Unit conversions verified (nN/nm -> pN/nm x1000; kPa -> 1e-3 pN/nm^2; pN/nm^2 -> 1e6 Pa).
  Step-ordering choices are the first reader's and are logged in `q_step_algorithm`; not changed.
- `clutch_no_talin_sim` (p. 4): unfolding switched off, as the text describes; not changed.
- `threshold_sensitivity` (p. 25): S = d log k_threshold / d log p, slope of a log-log linear fit, threshold at
  a 10% density rise; matches the printed definition. Grid and factors are added choices
  (`q_sensitivity_procedure`).
- `unfold_refold_crossing` (p. 5): closed form of k_unf = k_fold; with the added 2021 coefficients it gives
  about 5.07 pN, consistent with the cited 5 pN.
- Added coefficients (`koff_*_added`, `*_kunf*`, `*_kfold*`): conversions from /N to /pN checked
  (e.g. -1.601e11 /N = -0.1601 /pN; 1.786e12 /N = 1.786 /pN); `ksub_factor_added` 4π/9 = 1.396 checked.

## Runs checked

- Every Fig. 6 run uses its own panel's caption parameters (nf for a-c; kont and dadd for d-f; nm for g-i)
  and the Table 1 reference values otherwise; Fig. 3 runs use Table 1. No errors found.

## Changes made

- None to existing data, models, runs or comparisons: no transcription error was found.
- Added `q_audit_fig3a_left_out` (reading; p. 4): disagreement with leaving Fig. 3a out; its measured αvβ3
  lifetimes and the ref. 25 unfolding-time line should be read, and the line can validate the added k_unf law.
- Added `q_audit_rate_law_alternatives` (reading; p. 19): the added rate-law coefficients have no
  alternatives although every verdict rests on them; the second 2021 catch-bond fit is a real joint
  alternative.
- Added `q_audit_gpen_threshold` (reading; p. 7): the text's "no major change in the threshold" under GPen
  is consistent with the printed S values (the kont and dadd shifts cancel) but is not compared in the
  record; with the record's model it would not hold.

## Not checked / limits

- The figure readings (`figures/*.py`) were not re-run or overlaid: the `boxgraph figure` and `pdftoppm`
  commands were refused in this session. The reading positions, axes and crops in `figures.yaml` were looked
  at against the page images (Fig. 3d,e, p. 4; Fig. 6, p. 7) and are plausible, but the values were not
  independently verified.
- Supplementary Table 1 95% confidence intervals remain left out (first reader's scope; see source notes).
- The order-of-magnitude claim on p. 8 that talin carries "a few piconewtons" is not numeric enough for a
  verdict and was not recorded.
