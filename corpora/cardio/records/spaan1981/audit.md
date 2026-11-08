# Audit of spaan1981

Second reading against the page images (pp. 1, 4, 5, 6, 8, 9, 10) and the text of all ten pages.
Figures were not read (left to the figure job).

## Values checked, no transcription error found

- `capillary_diameter_used` (5), `capillary_density_used` (3500), `capillary_fraction_printed` (0.068),
  `artery_fraction_printed` (0.023), `total_blood_volume_morgenstern` (10 to 15), `area_fig4a` (0.13),
  `volume_variation_printed` (0.06), `lv_mass_fig4` (109): p. 8, all as printed.
- `tau_initial_fig7` (≃ 0.2), `tau_slow_fig7` (≃ 3): Fig. 7 caption p. 8 and text p. 9 both print ≃.
- `Ra_fig7` (≃ 65), `Rv_fig7` (≃ 35), `Cep_printed` (0.003), `Cep_arts` (0.002), `Cim_morgenstern`
  (0.085), `Cim_scharf` (0.08), `Cim_salisbury` (0.07), `tau_parallel_printed` (2): p. 9, as printed.
- `Cim_per_mass_printed`: p. 9 prints "approximately 0.07" in words; the record's "≈ 0.07" carries
  the same meaning (no verdict either way). Kept.
- `ra_rc_slope` (0.63), `ra_rc_intercept` (-12.9), `ra_rc_r` (0.939): p. 5 and Summary p. 1, as printed.
- `p_im_mean` (53.1 ± 7.02), `plv_systolic` (100 ± 10): p. 6, as printed. `wedge_pressure` (14): p. 10.
- References checked against p. 10 (Seely 1958, Berne and Levy 1972 are right; the OCR is wrong).
  The text cites "Bassingthwaighte, 1973" (p. 8) while the list prints 1974; the record keeps both
  as printed (label and text). No change.

## Models checked

- `potential_source_eq2`: Eq. 2 on p. 4 is p_lc = -q_c R_a + p_im, as recorded. Eq. 1
  (q_c R_s + q_c R_a = p_ib) is not a separate model; it feeds no printed number. No change.
- `resistance_split`: R_c = R_a + R_v, p. 4, as printed.
- `ra_rc_regression`: p. 5, as printed.
- `capillary_volume_fraction`, `small_artery_volume_fraction`, `compartment_volume_sum`,
  `volume_variation_amplitude`, `epicardial_capacitance_rc`, `intramyocardial_capacitance_rc`,
  `parallel_discharge_time`, `capacitance_per_mass`: from words on pp. 7-9; each matches the text.
- `waterfall_20_layer`: not runnable, p. 7; agreed.

## Added by the audit

- `ra_fraction_printed` (p. 9, "63% of the total resistance"): a printed result not yet compared.
  Added quantity `arterial_resistance_fraction`, model `ra_fraction_regression` (R_a / R_c from the
  regression, built from `ra_rc_regression`), added input `rc_for_fraction_added` (100 mm Hg s/ml,
  alternatives 60, 140, 1000), run `run_ra_fraction`, comparison `cmp_ra_fraction` and question
  `q_ra_fraction_rc`. It gives 0.50 at R_c = 100: not reproduced, consistent with the first
  reader's `q_ra_63_percent`.
- `eq2_fit_r_min` (p. 5, correlation coefficients "higher than 0.992" for the 18 Eq. 2 fits), with
  quantity `eq2_fit_correlation`: recorded for the figure reading of Fig. 5; no verdict (a bound).
- Question `q_regression_curves_fig4` (possible_error, p. 5): "Regression curves, as shown in
  Figure 4" should probably read Figure 5.
- Question `q_plm_95_condition` (reading, p. 9): the Fig. 7 condition is printed "P̄_lm = 95 mm Hg";
  the record's condition `mean_left_main_pressure: 95 mmHg` is a reading of it.
- Question `q_wedge_14_vs_measured` (unexplained_difference, pp. 1, 4, 10): the Summary defines R_c
  with a fixed 14 mm Hg; the Methods with a per-experiment wedge pressure.

## Disagreements with the first reader

- None that change a value. The added `lv_mass_fig7_added` (109 g) and its alternatives are a
  reasonable choice and are kept; the verdicts of `cmp_cim_morgenstern` and `cmp_cim_salisbury`
  depend on it (already covered by `q_lv_mass_fig7`).
- `potential_source_eq2` stays never run (warning): no printed number comes from it without the
  Fig. 5 points, which the figure job will read.

Validator: SOUND (0 errors, 1 warning: `potential_source_eq2` never run).
