# Audit of westerhof2009

A second, independent reading of the PDF (pages 1-11), checked against the page images of pages 2-8.

## Values checked (no change)

- Table 2 (p. 6): all twelve entries match the page, including signs: Zc +9/0/0, R +41/+90/-28,
  C -10/+22/+5, heart period -50/-90/28. `sens_t_sv` is unsigned on the page, as recorded.
- `factor4_printed` (p. 6) "a factor 4", `age_r_increase` "10–20%", `age_c_decrease_factor` "2–4": match.
- Fig. 8 labels (p. 6): C 57, 19, 4.8 (10^-3 ml/mmHg) and R 22, 46, 103 (axis label "R (mmHg/ml/s)"):
  match. The unit mmHg*s/ml is the same as mmHg/(ml/s).
- `td_8ms`, `f_10hz`, `delay_coeff_printed` "≈ 2.9", `delay_phase_10hz_printed` "about 30°" (p. 4):
  match. The OCR "10-3" is 10^-3 on the page.
- `wk2_phase_high_f_printed` "-90" (p. 3): matches (minus sign present on the page).
- `zc_fraction_r` "about 5–7%" (p. 4), `decay_delay_fraction` "about 10%", `svpp_overestimation` "60%",
  `b_often_assumed` "-0.01" (p. 7), `f_low_bound_hr` 0.2 HR and `f_high_bound_hr` 3 HR (p. 8): match.

## Models checked (no change)

- `resistance_mean` (p. 2): R = (Pao,mean - Pven,mean)/CO ≈ Pao,mean/CO, as printed.
- `compliance_svpp` (p. 2, p. 7): C = DV/DP, as printed.
- `wk2_diastolic_decay` (p. 2): Pdia(t) = Pes e^(-t/RC), as printed.
- `decay_intercept` (p. 7): P(t) = P0 e^(-t/RC) + Pi, as printed.
- `area_method` (p. 7): RC = integral P/(P1 - P2) dt, as printed.
- `liu_compliance` (p. 7): C(P) = b SV e^(bP) / [((As + Ad)/Ad - Zc SV/Ad)(e^(bPs) - e^(bPd))], matches
  the page term by term; units are consistent (Zc SV/Ad is dimensionless).
- `two_area_method` (p. 7): integral Q dt = C (P1 - P2) + (1/R) integral P dt, as printed.
- `zc_wave` (Fig. 5 caption, p. 3): Zc = PWV·ρ/A (OCR "PWVq/A"), as printed.
- `burattini_impedance` (p. 5): (a + jωb)/(1 + jωc), as printed.
- `delay_phase` (p. 4): 360 × td × f, as printed.
- `wk2_impedance`, `wk3_impedance`, `wk4_impedance` (Fig. 5, p. 3): no formula is printed. The circuits
  as drawn are C‖R; Zc in series with C‖R; and Zc with L drawn in parallel (the hydraulic drawing shows L
  as a bypass around Zc), in series with C‖R. The models match these circuits.
- `rel_burattini_form`: the mapping a = R + Zc, b = Zc R C, c = RC rewrites Zc + R/(1 + jωRC) exactly
  in Burattini's form.

## Additions

- Added `q_decay_intercept_p0` (p. 7), kind `reading`. With the intercept term, P(0) = P0 + Pi, so this
  P0 is not the start pressure that `diastolic_start_pressure` describes. The quantity assignment is
  the first reader's judgement, so I left it unchanged.
- Added `q_symbolic_limits_uncompared` (p. 3, 4, 5; Table 1), kind `reading`. The paper's 0 Hz and
  high-frequency statements (3WK gives R + Zc, 4WK gives R, Burattini gives R, the 2WK modulus becomes
  negligible) are symbolic, with no printed number, so no datum/comparison can be added. They are
  recorded for a later relation or limit check.

## Disagreements (no change made)

- `zc_fraction_r` (p. 4): printed "about 5–7%" is recorded as "5 to 7" without the approximate mark.
  `decay_delay_fraction` and `delay_phase_10hz_printed` record "about" as "~". The datum is not compared,
  so no verdict depends on it. I left it as entered.
- `delay_phase` (p. 4): a delay of flow behind pressure gives a phase lag. The paper prints the magnitude
  360 td f without a sign, and the model follows the printed form. No question needed, noted only.

## No new comparisons

The paper is a review. Its only printed numbers that its own models produce are the delay phase
(2.9 f, 30°), the factor 4 from Table 2 and the -90° limit, and all three are already compared. Every
other number is cited from other works or labels a figure whose model parameters are not given.
