# Audit of vink2024 (second reading, 2026-11-11)

Checked against the page images (pp. 1-6, 11) and the supplement text (pp. 9-19). No figures rendered or read.

## Transcription check: no corrections needed

- All values in `data.yaml` (Tables 1-2, p. 4; text 3.1-3.5, pp. 3-5; abstract, p. 1; Discussion, p. 6;
  Supplemental Tables 2-3, pp. 10-11) match the page images: digits, signs, units and pages. No value was changed.
- Models `mvr_ratio`, `heart_rate_reserve`, `hrr_age_adjusted` (p. 3, 2.4-2.5), `mbf_fold` (p. 16), `mbv_from_plateau`
  (p. 2, 2.3: y = A (1 - e^(-beta t))) and the processing models match the printed definitions. No model was changed.
- `added.yaml`: all six added inputs have a basis and real alternatives. No disagreement.

## Additions (printed results not yet compared)

- `txt_men_c_n`, `txt_men_c_pct` (p. 3) and `abs_men_c_pct` (p. 1): the controls' 6 men (21.4%, 21%); new run
  `run_txt_men_c_pct` and comparisons `cmp_txt_men_c_pct`, `cmp_abs_men_c_pct`.
- `txt_htn_a_pct`, `txt_htn_c_pct`, `txt_hlp_a_pct`, `txt_hlp_c_pct`, `txt_mvs_w_pct`, `txt_mvs_m_pct` (p. 3, 3.1):
  the text's 57% vs 0%, 50% vs 0%, 50% vs 0%; compared with the existing Table 1-2 percentage runs
  (`cmp_txt_htn_*`, `cmp_txt_hlp_*`, `cmp_txt_mvs_*`).
- `txt_age_*`, `txt_bmi_*` (p. 3) and `abs_age_a_m`, `abs_age_c_m` (p. 1): ages and BMI restated from Table 1;
  consistency comparisons `cmp_txt_age_*`, `cmp_abs_age_*`, `cmp_txt_bmi_*`.
- `s3_mbf_base_a_s`, `s3_mbf_base_c_s`, `s3_mbf_ins_a_s`, `s3_mbf_ins_c_s` (p. 11): the baseline and hyperinsulinemia
  MBF SDs, which were only in notes, now recorded as data.
- `perfused_capillary_share` (p. 6, "around half of the capillaries ... filled with blood", ref. 22) and
  `o2_extraction_rest` (p. 6, "up to almost 70-80% at rest", ref. 9): cited values at the capillary scale, recorded
  as reported, with new quantities `perfused_capillary_fraction` and `oxygen_extraction_fraction`.

## New question

- `q_perfused_capillaries_mbv` (reading, p. 6): the cited half-perfused capillaries widen the MBV magnitude gap
  (`q_mbv_magnitude`, `q_no_corpus_mbv_model`) for any capillary volume fraction computed from batch 10's fixed-tissue
  morphometry.

## Disagreements with the first reader

- None. The first reading's choices (ratio-of-means approximations for medians, added denominators 27/21/17/4,
  f = 1 for the age-predicted maximum heart rate, density 1.05 g/mL) are documented with alternatives and questions.
- Remaining warnings are expected: `hrradj_c_med` cannot be recomputed (`q_hrr_controls`), and the "inputs disagree
  on group" warnings come from total = group 1 + group 2 runs, which combine two groups on purpose.

Validator: `vink2024: SOUND (0 errors, 41 warnings)`.
