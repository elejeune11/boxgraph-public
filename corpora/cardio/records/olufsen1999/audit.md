# Audit of olufsen1999

A second reading of the paper (PDF pp. 1-12) against the record, made from the page text and the
110-dpi page images. Figures were not read; that is the next job.

## Checked, no change needed

- Every printed value in `data.yaml` agrees with the page images: digits, sign, power of ten, unit
  and page. That covers nu_blood, T_heartbeat, delta_bl_estimate, delta_bl_constant (p. 2);
  k1_fit, k2_fit (−22.53, misread by the OCR as 222.53) and k3_fit (p. 3); co_measured, co_scaled and
  co_reduction_printed (p. 4); d_arteriole, A_arteriolar_bed, n_terminal_printed, n_subtrees,
  gen_printed and xi_chosen (p. 6); eta_chosen, gamma_printed and lrr_iberall (p. 7); lrr_brachio,
  r_root_brachio and r_min_brachio (p. 8); co_reduction_discussion (p. 11). No transcription errors.
- Each model matches its equation as printed: stiffness_eq6 (Eq. 6, p. 3), asymmetry_eq21 (Eq. 21,
  p. 7) and structured_tree_impedance. For the tree model that means Eq. 16, Eq. 17 and Eq. 18 on p. 6,
  K of Eq. 12 and C on p. 5, c and g on p. 6, and alpha and beta on p. 7. Also checked:
  boundary_layer_lighthill (p. 2; it models the dimensionally consistent first form, and the misprint
  is already in q_boundary_layer_exponent), terminal_branch_count, generation_count (p. 6) and
  cardiac_output_reduction (p. 4).
- My own arithmetic agrees with the first reader's findings. Eq. 21 with xi = 2.76 and eta = 1.16
  gives gamma = 0.356, and gamma = 0.41 gives eta = 1.171 (q_asymmetry_eq21, p. 7). The factor 2 in
  the c0^2 formula is recorded (q_wave_speed_factor, p. 3).
- The added input rho_blood_added (1.05 g/cm^3) has a basis and real alternatives.

## Changes (additions; nothing was corrected or deleted)

- Added datum `lrr_default` = 50 (p. 8, "modify the length-to-radius ratio from 50 to 130"). It is the
  l/r of the trees other than the brachiocephalic one.
- Added data `r_min_r0`, `r_min_r1`, `r_min_r2`, `r_min_r3` = 0.06, 0.04, 0.02 and 0.01 cm (p. 9). These
  are the printed minimum radii of the Fig. 1 trees, now used by the runs below.
- Added datum `dc_radius_power_printed` = "≈ 3" (p. 9). This is the printed claim that the average
  impedance is "approximately inversely proportional to the root radius to the third power". It
  was a printed model result with no comparison. Added quantity `dc_impedance_radius_power`.
- Added model `dc_root_radius_power` (p. 9, from words, built_from structured_tree_impedance). It
  computes the two-point log-log slope of Z(0, 0) between two root radii.
- Added inputs `r_root_lo_added` = 0.1 cm and `r_root_hi_added` = 0.5 cm, with their basis and
  alternatives. The paper does not print the root radii behind the p. 9 claim.
- Added runs `run_dc_power_r0`, `run_dc_power_r1`, `run_dc_power_r2`, `run_dc_power_r3` and
  comparisons `cmp_dc_power_r0`, `cmp_dc_power_r1`, `cmp_dc_power_r2`, `cmp_dc_power_r3` (purpose
  approximation, p. 9). The printed ≈ 3 is approximate, so these comparisons get no verdict. The
  computed powers are about 2.1 to 2.55.
- Added question `q_dc_power` (unexplained_difference, p. 9) for that difference.
- Added question `q_continuity_eq13` (possible_error, p. 5). Eq. 13 is printed as "i omega/C P". That
  is not dimensionally consistent, and it disagrees with Eq. 14 and with c and g on p. 6. The tree
  model uses the p. 6 forms.
- Added question `q_cvol_derivative` (possible_error, p. 3). Cvol is printed as dp/dV, the inverse of
  a compliance. Also, 3 r0/(2 Eh) is a relative area compliance, not a volume compliance. So how the
  Fig. 3 estimates were made is not determined by the text.
- Added question `q_fig9_data_source` (reading, p. 8 and p. 9). The text says the measured impedance
  is "adapted from Nichols and O'Rourke (27)", but the Fig. 9 caption says "Mills et al. (26)".

## Disagreements with the first reader (recorded as questions, nothing changed)

- `q_boundary_layer_reading` (reading, p. 2): delta_bl_estimate is printed as "≈ 0.01", which gets no
  verdict. The tenfold disagreement (0.096 against 0.01 cm) is therefore carried only by
  q_boundary_layer_exponent and by the consistency comparison with "1 mm". This is a note for
  whoever reads the verdicts, not an error. The first reader's transcription is right.
- source.yaml gives `reader.model` as `None`. I left this as the first reader wrote it.
