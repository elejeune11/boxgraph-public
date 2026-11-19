# Audit of fierling2022 (second reading, 2026-11-19)

Checked each value in `data.yaml` that comes from text against its page image (pp. 3, 4, 5, 6, 9, 12, 18, 19,
23). Checked each model against its printed equation (pp. 4, 6, 17, 18, 20, 21). Figure readings were not
re-read; the next job reads figures.

## Transcription checks (no errors found)

- chi_nd, nu_2d (p. 5, Fig. 2 caption; also SI p. 19 "chi~_2D = 50 and nu_2D = 0"): match.
- eps_m_043 "0.43", eps_m_525 "5.25" (p. 5 caption; p. 23 caption): match.
- r_dv "90" um, axis_ratio_si "3", zp "0.45" (p. 18): match. gap_rel "2.5 x 10^-3", gap_si "≃ 0.2" (p. 18): match;
  the exponent is -3 on the image.
- gap_main "0.2 to 0.5" um (p. 3): match.
- width_fig1e "180", length_fig1e "500" um (p. 4, Fig. 1e): match.
- n_sagittal "3", n_cross "6" (p. 5): match. ventral_strain_example "25", stretch_*_printed "≈ 15", "≈ 5"
  (p. 23, Supp. Fig. 1c): match. The panel prints "–25%" and the caption "25%"; the record enters the magnitude,
  as its note says. The OCR of the p. 23 caption drops every digit, but the quotes used contain none.
- stretch_ratio_printed "about three" (p. 6), stress_ratio_twice "twice" (p. 5), area_reduction_text 20%/40%
  at 0/2 min (p. 9): match.
- myo_T "20" min, myo_Ic "4" (p. 12): match.
- prestress_main (p. 4): sigma_a = chi_2D (A_i - A_0)/A_0, epsilon_a = (A_i - A_0)/A_0: matches as printed.
- prestress_si (p. 21): sigma_a = chi_2D (gamma - 1)/gamma: matches as printed. gamma < 1 multiplies the Gram
  matrix of the unstrained facet (p. 20), so gamma = A_0/A_i is the record's reading. The last stress line on
  p. 21, chi_2D/gamma [Tr E - (gamma - 1)], is printed as the record says. The sign-corrected variant
  prestress_si_sign is kept beside the printed model, as it should be.
- strain_elastic_exp, strain_viscous_exp, strain_maxwell_exp (p. 17): match as printed, including the missing
  integration constants (q_strain_constants).
- myosin_eq1 (p. 6, Eq. 1): I_myo = I_c + I (e^{e^{(t - t0)/T} - 1} - 1): matches.
- embryo_dimensions (pp. 17-18): Gamma_0 matches. The printed pole position (±R_AP, 0, Z_p) is in units of
  R_DV (the surface gives z = Z_p R_DV there). This does not change L or W.
- vitelline_gap, length_compatibility, recoil_from_stress (p. 16 words), midline_stress_ratio, area_reduction:
  consistent with the text cited.

## Additions

- Model ap_stress_prestress, run run_ap_stress_prestress, comparison cmp_ap_stress_prestress (p. 6): the stated
  simulation result "The AP stress sigma_AP is found approximately equal to the pre-stress sigma_a" had not been
  compared. Midline band of Fig. 2c, from the existing readings. Question q_ap_stress_prestress.
- Comparison cmp_area_sim_muvi (p. 6): "the ventral region reduces in area showing similar dynamics as measured
  in vivo (Fig. 3a)": simulated against MuVi SPIM area, from the existing readings. Before this, area_sim_fig3a
  was only compared through the Discussion's 20%/40%. Question q_area_sim_muvi.
- Datum area_reduction_t0_def (p. 12): the 20% area reduction that defines t = 0. I did not add a comparison:
  area_reduction_text already compares 20% at t = 0 with both curves, and a table with only t = 0 cannot be
  compared with the two-point curves. Kept for question q_t0_wording.
- Datum relaxation_time_text "~1" min (p. 3, from ref-48): the relaxation time the paper states and uses to
  justify its elastic model. It is an input, and no model takes it.

## New open questions

- q_t0_wording (pp. 11, 12): t = 0 is defined as area "reduced by 20%" (p. 12) and as area that "reduces to
  20%" (p. 11).
- q_ap_stress_prestress (p. 6): sigma_AP 20.5 against sigma_a 21.3 at the midline; "approximately" has no
  stated tolerance.
- q_area_sim_muvi (p. 6): the simulated area reduction is ahead of the MuVi mean at t = 0 and behind it at 2 min.
- q_load_time_constant (pp. 12, 17): the SI viscoelastic argument needs t > tau, but tau is never stated for VFF.
  With Eq. 1 (T = 20 min), the effective tau near onset is about 20 min, longer than the plotted first phase.

## Disagreements with the first reading

- None on values or models. One judgement is left as recorded: the first reader adds no comparison for sdv_fig2c
  or sap_fig5d beyond the ratio and recoil runs. The paper's statements about sigma_DV are qualitative
  ("smaller than sigma_a" between 0 and pi/8, "greater" between pi/8 and pi/4) and need readings over the whole
  profile, which the next figure job can add.
