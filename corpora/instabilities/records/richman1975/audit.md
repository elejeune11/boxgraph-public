# Audit of richman1975

Second reading of PDF pages 1-4 against the record, from the page images.

## Checked, no change

- All twelve Table 1 areas (`area_I_normal` … `area_VI_microgyric`, p. 2): digits and unit (cm^2) match the image.
- `R_27wk` 84 mm, `t_27wk` ≈ 1.7 mm, `R_minus_2t_printed` 80.6 mm, `area_ratio_predicted` 1.04, `area_ratio_measured` 1.16 (note 18, p. 4): match.
- `t1_normal`, `t2_normal` 0.5 mm, `R_model` 25 mm (p. 2): match.
- `t_normal_fetus` ≈ 1.0 mm, `l_over_t_text` ≈ 8, `l_normal_predicted` ≈ 8 mm, `l_measured_27wk` 8.5 mm, `l_measured_sidman` 7.5 mm, `stiffness_factor_printed` 10, `wavelength_factor_printed` ≈ 2 (p. 3 text); `l_over_t_caption` 8 (Fig. 4 caption, p. 3): match.
- `E_white_matter_adult` 2 to 7 psi, `load_white_matter_adult` 1 to 10 psi (note 19, p. 4): match.
- Models `sphere_area_ratio` (4πR²/4π(R−t)²) and `sphere_area_ratio_approx` (R/(R−2t)), note 18, p. 4: match the printed equation, including the printed use of t (not 2t) in the exact form.
- Models `stratum_sum` (note 22, p. 4), `wavelength_from_thickness` (p. 3), `layer_area_ratio` (note 18): match.
- `plate_on_foundation`, `plate_stiffness_sensitivity`: from-words readings of unpublished ref. 20, flagged by `q_buckling_analysis_unstated`; the relation 1/lx² + 1/ly² = 1/l² and f(x,y) in their description match p. 2. Not changed (a judgement of the first reader).
- `added.yaml`: the three inputs (`Ecore_over_E1_added`, `E2_over_E1_added`, `stress_ratio_added`) have a basis and alternatives.
- Page 1: no numbers that feed a model.

## Changes

- Added datum `t2_absent` (0 mm), the paper's hypothetical "if in the microgyric brain t2 were to become 0" (note 22, p. 4).
- Added printed results `t_halving_printed` and `l_halving_printed` (0.5, printed in words "reduced by one-half", note 22, p. 4; also p. 3), quantities `thickness_reduction_ratio` and `wavelength_reduction_ratio`, model `reduction_ratio_note22`, runs `run_thickness_t2_absent`, `run_wavelength_t_sum`, `run_wavelength_t2_absent`, `run_reduction_note22`, and comparisons `cmp_t_halving`, `cmp_l_halving`.
- Added printed result `l_over_t_microgyric` (≈ 1 at sufficiently negative σ2/σ1, p. 3; note 23). Left uncompared: no model in the record produces it (validator warning expected); see `q_microgyric_l_over_t_not_modelled`. Fig. 4A in `figures.md` already lists it for the figure pass.

## New open questions

- `q_curvature_bound_1_100` (overstated_claim, p. 2): at the stated bound Ecore/E1 ≈ 1/100, the paper's own factor-of-2 sensitivity puts l near 16 mm, about two thirds of R = 25 mm, so "very short" wavelengths and neglected curvature are not shown there.
- `q_microgyric_l_over_t_not_modelled` (unstated_model, p. 3): the l/t ≈ 1 result rests on the unpublished analysis; the thin-plate reading cannot give it.

## Not added

- The symmetric solution lx = ly = l√2 (p. 3, Fig. 3B) prints no number; it follows from the relation already in `plate_on_foundation`'s description.
- "Ecore/E1 not less than about 1/100" (p. 2) is a condition, not a result; it is in `q_curvature_bound_1_100`.

No disagreement with the first reader's judgements.
