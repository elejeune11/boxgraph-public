# Audit of formaggia2003

Second, independent reading of `corpus/cardio/2003_Formaggia.pdf` against the record, done from
the page images. Figures were not read here; the next job reads them.

## Values in data.yaml

- Every printed datum checked against its page image, with no transcription errors found:
  zeta_flat, alpha_ref19 (p. 4, printed "1·1"); gamma_1_bif, gamma_23_bif, L_bif, E_bif (p. 14,
  3 x 10^6 dyne/cm^2); h0_bif, R0_bif, rho_bif, alpha_bif, nu_bif, T_bif, P_amp_bif (p. 15);
  L_endo, rho_endo, nu_endo, alpha_endo, h0_endo, E_endograft_endo (60 x 10^6), E_vessel_endo
  (10 x 10^6), R0_12_endo, R0_34_endo, R0_56_endo, T_endo, P_amp_endo (p. 16). Digits, signs,
  exponents, units and pages all agree. No changes made.
- The model settings taken from the text agree with the pages: endograft_bifurcation dt = 1e-5 s
  and 546 nodes (p. 16); newton_tol 1e-8 (p. 13). The bifurcation test's dt = 1e-5 s also matches
  the inertia tests' step (p. 20), and h = 0.1 cm matches the viscoelastic test's grid (p. 21),
  as q_bif_numerics says.
- I did not check the legend values alpha2_legend_zero, alpha3_legend_three and alpha3_legend_zero
  (p. 15/16): the legend is too small to read at page-image resolution, and reading figures is the
  next job's work.

## Models

- alpha_profile (p. 4): matches the printed s(x) = zeta^-1 (zeta + 2)(1 - x^zeta) and
  alpha = (zeta + 2)(zeta + 1)^-1. No change.
- bifurcation_angles (pp. 7-15): checked against Eqs. 3, 9, 10, 14 (F_Q = Q^2/A + beta A^(3/2)/(3 rho A0)),
  16 (H21), 18, 19, 22-23 (F_LW, B_LW, weak-form signs, P1 mass matrix), the first-order characteristic
  extrapolation (p. 10), 34 and 35-37 (loss terms -sign(u1) gamma1 u1^2 and +sign(ui) gamma_i ui^2
  sqrt(2(1 - cos alpha_i))). All agree with the equations as printed, and no corrected equation
  is used. No change.
- endograft_bifurcation (p. 16, Fig. 10 p. 17): the topology Omega_1 -> Omega_2 -> {Omega_3, Omega_5},
  Omega_3 -> Omega_4, Omega_5 -> Omega_6, with endografted domains 2, 3 and 5, matches Fig. 10 and the text.
  Interfaces with zero losses give Eqs. 32 and 38. No change.
- Added question q_eq15_friction_sign (p. 7): Eq. 15 prints B_Q = +K_R Q/A, but Eq. 3 implies
  -K_R Q/A. Both models follow Eq. 3. This is a sign inconsistency between two printed equations, so
  it does not change any model.

## Printed results not compared

- I found no further printed number that a model in the record produces from printed inputs. The
  remaining printed numbers are the inputs of the Section 4 wall-model tests: R0 = 0.5 cm, E = 3 x 10^6,
  dt = 1 x 10^-5 s (p. 20) and 1 x 10^-4 s, dx = 0.1 cm (p. 21), gamma = 3 (p. 22), and the
  stented-artery set-up (p. 23). They also include the claims "of the order of 10^-3", "less than 1%",
  "below 10%" (p. 21) and "differ less than one percent" (p. 13). The first reader left these out of
  scope as not runnable (q_wall_models_not_run, q_wall_claims). I agree and made no change.
  q_wall_claims does not list the claim "below 10%" (p. 21) against a 2D FSI code, but that claim
  is a comparison with an outside code and has no inputs to run.

## Unstated inputs (added.yaml)

- R0_2_added, R0_3_added, alpha3_text_zero: each has a basis and the printed alternative. angle_pi4
  has no alternatives, which is correct because it is an exact rendering of pi/4. K_R, dt and mesh,
  pulse shape and the outlet treatment are recorded as questions (q_kr, q_bif_numerics,
  q_pulse_shape, q_outlet_condition). No disagreement.

## Open questions added

- q_eq15_friction_sign (possible_error, p. 7): see Models above.
- q_eq4_area_integral (possible_error, p. 4): Eq. 4 prints the area as an integral of "dz", and
  Q has a dangling "A u-bar". These are typesetting slips and affect no model.

## Other notes (no change)

- source.yaml has reader.model: null. I left it as the first reader wrote it.
