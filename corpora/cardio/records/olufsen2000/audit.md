# Audit of olufsen2000 (second reading)

Second, independent reading of `corpus/cardio/2000_Olufsen.pdf` (PDF pp. 1-19) against the record, from the
page images. Figures were not rendered or read (left to the figure job).

## Values (`data.yaml`), checked against the page images

- `nu_printed` (p. 4): 0.046 cm^2/s. Correct.
- `T_printed` (p. 4) and `T_fig3_caption` (p. 7): 1.1 s. Correct.
- `delta_printed` (p. 4): "≈ 0.1" cm, formula (nu/omega)^(1/2) = (nu T/(2 pi))^(1/2). Correct.
- `rho_printed`, `mu_printed` (p. 10): 1.055 g/cm^3, 0.049 g/(cm s). Correct.
- `xi_printed` 2.76, `eta_printed` 1.16, `gamma_printed` 0.41, `alpha_printed` 0.9, `beta_printed` 0.6,
  `lrr_printed` ≈ 50 (p. 7). Correct.
- `k1_printed` 2.00 x 10^7 g/(s^2 cm), `k2_printed` -22.53 1/cm, `k3_printed` 8.65 x 10^5 g/(s^2 cm) (p. 5):
  exponents and sign checked on the image (OCR "107", "105", "⫺22.53"). Correct.
- `K5_printed` 0.75, `K2_printed` 0 (p. 6). Correct.
- `heart_rate_results` (p. 11), `heart_rate_appendix` (p. 14): 51 per minute. Correct.
- `r_t_ascending_aorta` (p. 11, Table 1 vessel 1): 1.25 cm. Correct.
- `A_aortic_root_printed` (p. 10): 5 cm^2. Correct.
- `p_systolic_cuff`, `p_diastolic_cuff` (p. 11): 120/80 mmHg. Correct.
- No transcription errors found; no value changed.

## Models, checked against the printed equations

- `boundary_layer_lighthill` (p. 4): matches delta = (nu T/(2 pi))^(1/2).
- `kinematic_viscosity` (p. 3): nu = mu/rho, as printed.
- `asymmetry_eq21` (p. 7): matches Eq. 21, eta = (1 + gamma)/(1 + gamma^(xi/2))^(2/xi).
- `scaling_eq22` (p. 7): matches Eq. 22, alpha = (1 + gamma^(xi/2))^(-1/xi), beta = alpha sqrt(gamma).
- `circle_area` (p. 3): A = pi R^2, as printed.
- `period_from_heart_rate` (p. 11): T = 1/HR (definition); port units 1/s, the datum is in 1/min and is converted.
- `network_1d` (pp. 3-10, 15-18): the stated equations (6), (13), (14), (15), (16)-(18), (38) and the taper law
  agree with the pages; Eq. B2 repeats the right-hand side of Eq. 13 and f(r0) = 4Eh/(3r0) (below B8) agrees
  with Eq. 14. Not runnable, as the first reader recorded; I agree.
- No model changed.

## Printed results the record does not compare

- Eq. 29 (p. 8), the small-w0 expansion of Eq. 28: checked by hand, not added. With
  F_J = 1 + w0^2/8 + w0^4/48 + ..., w0^2 F_J/(2(1 - F_J)) = -4 + w0^2/6 + O(w0^4), as printed. It is a symbolic
  identity with complex argument and no printed number, so I added no datum or comparison.
- The intermediate expansions of the large-artery derivation (p. 4: q = A u(1 - delta/R), the 1 - 4/3 delta/R
  and 1 + 2/3 delta/R factors) and Eq. 30's compliance (p. 8): checked by hand, and they follow from Eqs. 10 and 14.
  Eq. 30 writes p where Eq. 14 has p - p0; this is notation and needs no question. Nothing added.
- The count (n+1)(n+2)/2 of subtree impedances (p. 10): correct, as an identity. Nothing added.
- Fig. B4 and Algorithm 1 (p. 17) repeat the Table 1 geometry of vessels 5, 6, 7 (1.8/1.14/1.11, 19.0/0.29/0.28,
  1.0/1.11/1.09), and the 7 cm jump in the Fig. 4 caption (p. 11) equals the Table 1 length of vessel 1. These are
  repeated inputs, not model results, so they are not compared.

## Unstated inputs

- `added.yaml` is empty. Every comparison in the record runs on printed values only. The inputs the main
  model lacks (p0, numerics, connectivity) are recorded in `q_network_not_runnable`. I agree.

## Questions

- Added `q_figB4_labels` (possible_error, p. 17): the Fig. B4 label '(r_b)5 = 1.09 cm' appears to be a misprint
  for (r_b)7 (Table 1, Algorithm 1), and the caption says 'diameters' for values that are radii.
- The existing questions (`q_gamma_eq21`, `q_period_heart_rate`, `q_rmin_count`, `q_subject_age`,
  `q_network_not_runnable`, `q_cuff_pressure_claim`) agree with my reading of pp. 7, 10, 11, 14, 18; no disagreement.
