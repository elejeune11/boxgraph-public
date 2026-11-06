# Audit of craig2015

Second, independent reading against the page images (2026-11-01).

## Checked, no change needed

- `data.yaml`: every printed value checked against the page images, pp. 2, 5, 7, 8, 10, 12, 13, 14, 17, 18.
  Digits, signs, powers of ten (`drag_scale_printed` 10^3, `eta_ref29` 2 x 10^3, `viscosity_printed` 10^3)
  and units are as printed. I found no transcription errors.
- `clutch_profile` / `clutch_peak` (p. 7): Eqs. 5-9 as printed (lambda V'' = T - F dM/dx; M = 1 - gamma d(VM)/dx;
  N = (1 + bF dM/dx) exp(-V/v*); T = N V) and the boundary conditions (pp. 5-6) match.
- `uniform_flow_eq10` (p. 10), `hill_eq11` (p. 11), `lamellipodial_width` (p. 11, X ~ sqrt(2 mu V(0) / T-bar)),
  `lambda_estimate` (p. 7 definition of lambda, p. 8 numbers), `transport_epsilon` (p. 13-14, eps = V0 / (r L0)):
  each model matches the printed equation.
- `added.yaml` (`width_added`, `gradient_added`, p. 12): both have a basis and real alternatives.
- Figure readings: axes, panels and pages (pp. 10, 20, 21, 23) agree with the images. I did not re-run the
  overlays.

## Additions

- `V_lamella_ptk1` (p. 8): added the printed ~2 nm/s lamellar flow of Ptk1 cells. The basis of
  `gradient_added` uses it, but it had no datum.
- `vpeak_b0_text` (p. 12), run `run_vpeak_b0_text`, comparison `cmp_vpeak_b0_text`: Appendix A.2 says that
  with b = 0 the traction is "maximal for V~ = v*", a printed model result that was not compared. It now has
  a datum, a run and a comparison. The run uses the supplemental figure 2 parameters with lambda = 3. The
  model gives V~/v* = 0.98 at the 40-segment grid.
- `q_fmyo_analytic` (p. 10, possible_error): the printed F~myo = F exp(-x~/(gamma V~)) lacks the factor
  1/(gamma V~) that follows from Eq. 6 and the printed M~.
- `q_fig4f_vs_S4a` (pp. 10, 18, 23, possible_error): supplemental figure 4(a) at b = 0 and Fig. 4(f) at F = 1
  should coincide under their captions, but read about 4.3 um and 2.3 um. The model gives 4.2 um (lambda = 3) and
  2.4 um (lambda = 1). This is independent support for `q_fig4def_lambda`.
- `q_S3_vstar` (p. 18, possible_error): the supplemental figure 3 caption gives v* = 3, while everywhere else
  v* = 0.3. This is a possible misprint, and that figure is not in the record.

## Disagreements with the first reading (no change made)

- `q_S2c_near_edge` (p. 12): says the peak height v*/e is "as the paper states". The paper states only that
  the peak lies at V~ = v*. Recorded as `q_audit_vstar_over_e` (reading).

## Validation

- `.venv/bin/boxgraph validate records/craig2015`: SOUND (0 errors, 0 warnings).
