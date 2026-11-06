# Audit of olufsen2004

A second, independent reading against the page images (pp. 1-20, with images opened for
pp. 4, 6, 7, 8, 9, 13, 18). Figures were not read (left for the figure job).

## Values checked, no change

- `rho_blood`, `mu_blood`, `nu_blood` (p. 4): 1.06 g/cm^3, 0.049 g/cm/s, 0.046 cm^2/s match the image.
- `beta1`, `beta2`, `beta3` (p. 6): 2.40483, 5.52008, 8.65373 match.
- `lambda_q_first_printed`, `lambda_p_first_printed` (p. 7): "≈ 0.1729", "≈ 0.0075" match, approximation sign as printed.
- `lambda_q1_printed`, `lambda_q2_printed`, `lambda_p1_printed`, `lambda_p2_printed` (p. 8, Eq. 20): 0.1729, 0.0328, 0.0378, 0.0013 match.
- `lambda_q_sum_printed`, `lambda_p_sum_printed` (p. 13): 0.2057, 0.0392 match.
- `heart_rate_fig2` (p. 8), `R_large_vessel` and `order_needed_R15_printed` (p. 9), `R_threshold_quasisteady_printed` (p. 8), `R_threshold_first_order_printed` (p. 3): match.
- No transcription errors found in `data.yaml`.

## Models checked, no change

- `timescales_first_order` (p. 7, Eqs. 17-18): A = 1 - 32/beta_1^4, lambda_q = 1/beta_1^2, lambda_p = A/beta_1^2, as printed. I also re-derived Eq. 17 from Eqs. 15-16: it is consistent.
- `timescales_second_order` (p. 7, Eq. 19; p. 9, Eq. 24): the coefficients match the printed Eq. 19. I re-derived them from Eq. 14 truncated at n = 2: they are consistent.
- `kinematic_viscosity` (p. 4), `j0_zeros` (p. 6), `tau_crossing_radius` (p. 8, tau = T nu/(2 pi R^2)) and `order_needed` (p. 9): match the printed formulas and words.
- Eqs. 27 and 30 (p. 11) are not modelled: they have no numbers. I checked them against Eqs. 25, 28 and 29 and they are consistent.

## Changes

- Added datum `lambda_q_first_p73_printed` (p. 13): "0.1729", the first-order lambda_q, printed here without the approximation sign. Added comparison `cmp_lambda_q_first_p73` against `lambda_q_first_pred` (until now this value was only recorded as "≈ 0.1729", which gets no verdict).
- Added datum `heart_rate_fig2_per_s` (p. 8): "1" beat/sec. Added comparison `cmp_heart_rate_units` (consistency) with `heart_rate_fig2` (60 beats/min).
- Added question `q_appendix_series_sign` (possible_error, p. 18): the third line of the Appendix A expansion of K(s) has the wrong signs on its s^2 and s^3 terms. The line above it and the line below it both give s/8 - s^2/48 + 11 s^3/3072 (checked with sympy). No printed number depends on it.
- Added question `q_stergiopulos_factor` (reading, p. 11): "4/3 instead of 8 lambda_q, which is slightly higher" is ambiguous. 8 lambda_q is about 1.383, so the claim holds only if "which" means 8 lambda_q.

## Disagreements and notes (no change)

- `added.yaml` is empty. I agree: every input used (nu, HR, beta_n, R = 1.5 cm) is printed.
- `q_threshold_choice` (p. 9): this is the first reader's choice of crossings. I agree it is a reasonable choice and left it as it is.
- `source.yaml` gives `reader.model: None`. This is metadata of the first reading, so I left it unchanged.
- The windkessel claim of a "negative resistance and compliance" (p. 15) is qualitative. I checked it while reading: matching lambda_q = 0.1729 > lambda_p = 0.0075 with alpha = pi/8 gives R2 < 0 and C1 < 0, which agrees with the paper. There is no printed number to record.
