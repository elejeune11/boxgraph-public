# Audit of stergiopulos1999

Second, independent reading of `corpus/cardio/1999_Stergiopulos.pdf` (PDF pp. 1-8) against the record.
Figures were not read in this audit.

## What was checked and found right

- Every value of Tables 1-3 (p. 3, p. 5, p. 6): all 105 table entries in `data.yaml` (`hr_*`, `rp_*`, `rc_*`,
  `c*_*`, `l_*`, `rmse_*`, `aic_*`, `sc_*`), checked programmatically against the text and by eye against the page
  images. There are no transcription errors. The text layer is typeset, not OCR, so exponents are not at risk.
- The P values `p_rc3_results`, `p_c3_results` (p. 4), `p_c4_results`, `p_rc4_results` (p. 3) and the abstract P values
  `p_c3_abstract`, `p_c4_abstract`, `p_rc3_abstract`, `p_rc4_abstract` (p. 1) match the page images.
- The percentages `dev_c_4wk_human`, `over_c_3wk_hA`, `over_c_3wk_hC`, `under_rc_4wk_human`, `dev_rc_3wk_human`,
  `under_rc_3wk_dm`, `over_c_3wk_dm`, `dev_l_4wk_dm`, `under_c_4wk_dm` and `under_rc_4wk_dm` (p. 4) match the page image
  (OCR "," is "<" and "~").
- `p_3wk`, `p_4wk` (p. 2) are correct as stated in words.
- `info_criteria_eq2_3` matches the RSS and RMSE definitions and Eqs. 2-3 on p. 2. `zin_3wk` and `zin_4wk` match the
  Fig. 1 schematics (p. 3): R_c parallel to L, in series with R_p parallel to C. `ttest_*` and `reldev_*` follow the
  words on p. 2 and p. 4.
- The heart-rate column header on p. 3 does read "beats/min" on the page image, so `q_hr_unit` stands.
- The added sample counts `n_*` have a basis and alternatives. `q_sample_count` states how the N were chosen to fit
  the AIC.

## Changes

- `inertance_eq1` (p. 2, Eq. 1): equation string changed from `(rho c_u) integral_0^{l_s} dx/A(x)` to the printed
  form `integral_0^{l_s} c_u rho/A(x) dx`. The two are mathematically the same, but the record must hold the equation
  as printed.
- Added data `mass_d71` ... `mass_d79` (p. 3, Table 1, body mass) and quantity `body_mass`. These now feed question
  `q_l_body_mass`.
- Added data `l_4wk_hA_text`, `l_4wk_hC_text` (p. 4): the text repeat of the human L values. Added consistency
  comparisons `cmp_l_4wk_hA_text_vs_table`, `cmp_l_4wk_hC_text_vs_table` against Table 2.
- Added inputs `p_3wk_with_rp` = 3 and `p_4wk_with_rp` = 4 (`added.yaml`), with runs `run_ic_{3wk,4wk}_<beat>_prp`
  for all nine beats and comparisons `cmp_{aic,sc}_{3wk,4wk}_<beat>_prp` (p. 2, Eqs. 2-3; Tables 1-2). These are
  alternatives, not replacements: the first reader's P = 2, 3 runs are untouched.

## New open questions

- `q_sc_param_count` (unexplained_difference, p. 2): counting R_p in P (P = 3 and 4) brings the computed SC within
  about 1 of the printed SC for dogs 72, 76, 78, 79 (three-element) and both human beats, using the first reader's
  N. Dog 74 instead matches P = 2 and 3. This refines `q_sc_inconsistent`: a different P count, not a different N,
  may explain most of the SC differences.
- `q_l_body_mass` (overstated_claim, p. 6): "inertance appears to decrease with increasing body mass (Table 1)". For
  the seven dogs, r is about -0.61 with P about 0.14, which is not significant.
- `q_sensitivity_unrecorded` (reading, p. 4): the dog 71 sensitivity percentages (11, 20, 5%) are printed model
  results left unrecorded. They could be reproduced once Fig. 1 is read.

## Disagreements (no change made)

- The first reader left out the sensitivity percentages (p. 4) and body mass. I added body mass, because a claim now
  depends on it. The sensitivity numbers stay out (see `q_sensitivity_unrecorded`), because the scope is the first
  reader's.
- `source.yaml` gives `reader.model` as `None`. This is left as it is, as provenance of the first reading.
- Fig. 2 (p. 4) shows the dog means ± SE of Table 1. The quantities `mean_*` and `sem_*` exist, but no model computes
  a mean or an SE from Table 1. When the figure job reads Fig. 2, a mean/SEM processing model over the seven dogs
  would make those readings comparable (consistency).
