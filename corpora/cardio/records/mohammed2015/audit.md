# Audit of mohammed2015 (second reading, 2026-11-11)

Checked against the page images: pp. 1, 3, 4, 5, 7, 8, 12, 13, 14, 15, 16 (every value of data.yaml on
those pages; pp. 18-19 checked through their quotes). No transcription error was found: every number,
sign and page of the first reading matches the page image, and the models (circle_area, relative_reduction,
relative_increase, percentage, count_sum, count_difference, vessel_share, same_density) are the stated
relations as printed. Nothing was changed or removed.

## Added

- **Table 3 R2 check** (p. 5): data `b_mvd_group`, `se_mvd_group`, `b_pehw_group`, `se_pehw_group`,
  `b_cad_group`, `se_cad_group`, `r2_cad_group`, `b_fib_group`, `se_fib_group`; models `r2_group_mvd`,
  `r2_group_pehw`, `r2_group_cad`, `r2_group_fib` (R2 = t^2/(t^2 + n - 2), the one-predictor OLS identity;
  one model per coefficient quantity so units stay checked); runs `run_r2_*`; comparisons
  `cmp_r2_mvd_t`, `cmp_r2_pehw_t`, `cmp_r2_cad_t`, `cmp_r2_fib_t`. MVD reproduces (0.230); the CAD
  row (SE printed 0.02) gives 0.98 against 0.30 (question `q_table3_cad_se`); % expected HW 0.393 and
  fibrosis 0.082 are near 0.40 and 0.09 (`q_table3_r2_close`).
- **Added input** `n_regression_added` (228, alternatives 223 and 207) in a new `added.yaml`: Table 3
  does not print the n of each regression.
- **Fibrosis medians repeated in the Discussion** (p. 8): `fib_c_med_disc`, `fib_h_med_disc`, compared
  with Table 2 (`cmp_fib_c_discussion`, `cmp_fib_h_discussion`).
- **Age at death of the HFpEF group** (Table 1 p. 4, Table S4 p. 16): `age_death_h_*_t1`,
  `age_death_h_*_s4`, comparisons `cmp_age_h_med_s4`, `cmp_age_h_q25_s4`, `cmp_age_h_q75_s4`.
  Quartiles differ (68–85 vs 66-83); question `q_age_death_s4`.
- **Quantities** `mvd_group_coefficient`, `pehw_group_coefficient`, `cad_score_group_coefficient`,
  `log_fibrosis_group_coefficient`, `age_at_death`.

## Questions added

- `q_table3_cad_se` (possible_error, p. 5): CAD score SE 0.02 inconsistent with R2 0.30.
- `q_table3_r2_close` (unexplained_difference, p. 5).
- `q_table3_half_difference` (reading, p. 5): Table 3 group coefficients are about half the Table 2
  group differences (suggests -1/+1 coding); the implied residual SD of MVD (about 284/mm2) supports
  `q_mvd_h_q75` (HFpEF upper quartile 1370 looks too high). Fig. 4A (p. 7) also shows the HFpEF box top
  near 1200, by eye only; the figure reading job should settle it.
- `q_age_death_s4` (possible_error, p. 16).

## Disagreements with the first reading

- None on values or models. Left as the first reader chose (not entered, could be added later):
  % expected HW in HFpEF with/without stenosis 168 [144–206] / 168 [144–195] and EF 40-49% 166 [148–197]
  (p. 3), the literature collagen volume fractions 2%–13% and 2%–4% (p. 8), and the 35% height-indexed LV
  mass increase cited from ref 2 (p. 7); none is a result of a model in this record.
- Batch 10 cross-record checks: the first reader's validations of the control and HFpEF capillary
  density against rakusan1992 and kaneko2011 are in place with their conditions; campbell2011 reports a
  length density, a different quantity, and is rightly not compared. No model in this record predicts
  a myocardial blood volume (vink2024); MVD is a profile count per area, not a volume fraction.
