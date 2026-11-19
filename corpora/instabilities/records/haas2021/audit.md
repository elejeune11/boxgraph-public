# Audit of haas2021

A second, independent reading, checked against the page images.

## Checked, no change

- data.yaml, all 19 original values (p. 11: k(0) = 13/5, k(±1) = 3, ν = 1/2, E = 3C, 4C(εh), C(εh)^3/3; p. 12: εh = 0.15; p. 13: κp = κa = 1, κb = −2 and −8.5, fp = 0.8, fa = 1, s0 = 1.5, w = 0.2 and 0.5). Digits, signs and pages agree with the page images. No transcription errors.
- coeffs_eq58 (p. 9, Eqs. 58a–58j): every numerator, denominator, sign and tanh⁻¹ term agrees with the page image.
- coeffs_bar_eq64, coeffs_bar_combined (p. 10, Eqs. 64a–64d): both equalities as printed. I checked by hand that 64c follows from 58d and 58h.
- energy_eq63 (p. 9 Eq. 63; p. 10 Eqs. 65, 66a–66c): unbarred α_φφ, β_φs, β_φφ and γ's are used where the paper prints them unbarred. The prefactors are as printed.
- stretch_discriminant_printed (p. 10): −48(1 − η²)^−2 as printed.
- energy_eq67_classical (p. 11, Eqs. 67, 69a, 69b): as printed. The duplicated label ê0,stretch on Eq. 69b is already recorded (q_eq69b_label).
- energy_eq70 (p. 11, Eqs. 70a, 70b): as printed, without prefactors on the correction terms. The variant energy_eq70_prefactors and q_eq70_prefactor are justified by a dimension argument.
- k_eq71 (p. 11, Eq. 71): as printed.
- neohookean_modulus and classical_moduli (p. 11; Eq. 26 on p. 5): agree with the text.
- volvox_invagination (pp. 12–13): agree that it cannot be run (q_volvox_not_rerun).

## Added

- eta_eq59 (p. 9, Eq. 59): a new model η = κs0 (εh)/(2 fs0 fφ0), the middle form of Eq. 59.
- eta_fig5b_printed, eta_fig5e_printed (p. 13): η = −0.23 and η = −0.99, printed as panel labels in Fig. 5(b) and 5(e). They are not in the text layer; I read them from the page image. Runs run_eta_fig5a and run_eta_fig5d; comparisons cmp_eta_fig5b and cmp_eta_fig5e.
- f_s0_bend_added, f_phi0_bend_added (added.yaml; p. 12 Fig. 4(h), p. 13): fs0 = fφ0 = fp = 0.8 in the bend region, read from the Fig. 4(h) schematic. Alternative: 1 (fa).
  - −0.23 is reproduced: the computed value is −0.234.
  - κb = −8.5 gives −0.996, which rounds to −1.00, not the printed −0.99. Recorded as q_eta_fig5e (unexplained_difference).
  - The reading of where η is evaluated is recorded as q_eta_label_location (reading).
- volume_conservation_region and volume_conservation_extent (p. 19, App. A: Eqs. A36, A37b and the conditions stated in words; Fig. 6(b)): two new models with `from_words: true`. These printed results were not in the record. They are compared with:
  - K0h2_zero / hH0_max_K0zero_printed: |hH0| ≤ 1 for K0 = 0;
  - K0h2_min_x9_printed: h²K0 > −16/9, recorded as −16;
  - omega_x9_printed: ω = 64/9, recorded as 64;
  - sqrt_omega_x3_printed: √ω = 8/3, recorded as 8.

  The computed values are 1, −16.000, 64.000 and 8.000. Runs run_volume_K0zero and run_volume_extent; comparisons cmp_volume_*. New quantities: scaled_gaussian_curvature, scaled_mean_curvature, scaled_gaussian_curvature_times_9 and scaled_mean_curvature_times_3. The scaling of the fractions is recorded in q_fractions_audit (reading). The reading of the monotonicity condition, on which ω rests, is recorded in q_volume_region_from_words (unstated_model).

## Disagreements and remaining points

- None with the first reader's judgements.
- The nine "never run" warnings are for models tested only through relations (same_as / reduces_to). They were already there and are left as they are.
- Fig. 3 (p. 10) and the Fig. 5 curves are for the figure job. I did not read them, as instructed.
