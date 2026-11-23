# Figure readings of alonsomatilla2023

Lines are read with `figures/_fig.py` (MATLAB-style panels: the box's left and bottom lines,
inward tick marks pooled from both sides of the box, the series by its colour from a seed
point). Symbols are read with `figures/_marks.py` (axes by `_fig.calibrate`; symbols as
connected groups of the series colour, filled ones told from open ones by the ink in their
centre, a same-coloured line traced and removed first where one runs through them; groups
much larger than the median symbol are two symbols drawn over each other and are left out).
Every reading was checked on its overlay (`figwork/<reading id>.png`); misfits are the largest
residual of the axis fit, in pixels at the reading's dpi. The paper has no measurements: every
plotted value is a model result (mean-field, analytical or stochastic).

## Read

First pass (unchanged):

- Fig. 1(B): `fig1b_F1`, `fig1b_F10` (yellow F = 1, dark green F = 10), K <= 0.01; log10 x from
  the long decade ticks, misfits about 1 px. The F = 1 fall between K = 0.005 and 0.02 is not
  read (near vertical, covered by symbols).
- Fig. 2(F): `fig2f_tau10`, the Eq. 6 line for tau = 10.
- Fig. 4(A) left: `fig4a_T_tau50`, `fig4a_T_tau5`; Fig. 4(A) middle: `fig4a_nb_tau20`;
  Fig. 4(B) left: `fig4b_T_tau50`.
- Fig. 5(B): `fig5b_tau100`, `fig5b_tau10`; Fig. 5(C): `fig5c_tau100`.

Second pass:

- Fig. 2(C), dashed line (Eq. 5): `fig2c_eq5`, read half-way between the symbols at
  tau = 0.5 ... 9.5; x from the tick at 5 and the box lines at 0 and 10 (misfit 0.5 px), y from
  the ticks at 0.2-0.6 and the box lines at 0 and 0.8 (misfit 3.3 px). Run against
  `critical_activity_eq5` with the printed C1 = 0.4 (`cmp_fig2c_eq5_line`). The line is
  C1 tau/(tau + 1) with C1 = 0.30 at every read position (0.0998/0.333, 0.181/0.6,
  0.272/0.905), not 0.4: this settles `q_eq5_vs_fig1b` (see `q_fig2c_c1`).
- Fig. 2(C), symbols: `fig2c_soft_w200` (solid red circles, 10 of 10), `fig2c_soft_w2000`
  (solid green triangles, 8 of 10: tau = 2 is hidden under a solid blue diamond, tau = 4 is
  drawn over an open triangle), `fig2c_rigid_w200` (open red circles, 10), `fig2c_rigid_w1000`
  (open blue diamonds, 9: tau = 1 is under an open triangle), `fig2c_rigid_w2000` (open green
  triangles, 10). The solid blue diamonds (omega = 1000, soft) lie under the solid green
  triangles and are left out. Eq. 5 is compared with the soft symbols as `fit_quality` (C1 was
  fitted to them). The rigid (open) symbols are recorded as `critical_myosin_activity_rigid`;
  no model in the record gives the rigid critical activity (the paper defines it only through
  its numerical results), so they have no comparison.
- Fig. 2(F), symbols for tau = 10: `fig2f_mf_tau10` (open squares, the mean-field optimum, at
  omega = 400, 800, 2000; the others are covered by the line or by a solid circle) and
  `fig2f_st_tau10` (solid circles, the stochastic optimum, at omega = 300 and 600; those at
  1000, 1400, 1800 sit on the line). The Eq. 6 line of the same colour is traced and removed
  before the symbols are grouped. Compared with Eq. 6 as `approximation` (settles part of
  `q_fig2f_symbols`).
- Fig. 4(B) left: `fig4b_T_tau20` (magenta, after its drop near F = 1.1; below it the line runs
  under the others); Fig. 4(B) middle: `fig4b_nb_tau50` (olive). Same calibration as the first
  pass (misfits 0.9-2.6 px). Both run with `rigid_steady_state`.
- Fig. 5(A): `fig5a_tau1`, `fig5a_tau5`, `fig5a_tau10`, `fig5a_tau20` (F_opt against omega),
  read between the symbols; x from the ticks at 200-800 and the right box line at 1000
  (misfit 0.5 px), y from the ticks at 1-3 and the box lines (misfit 1.4 px). Run with the new
  `rigid_optimum_activity` (the maximum over F of the S31-S36 traction), as the caption defines
  F_opt.
- Fig. 5(B), inset: `fig5b_inset` (dark-blue dots, omega_opt against tau; 10 of 12 read, the
  others covered by the grey dashed line), rendered at 2400 dpi; the inset is a bitmap of
  8-px blocks at that dpi, which the interval includes. Grey box lines and ticks, calibrated
  with a lighter ink threshold (misfits 1.3 px x, 0.9 px y). Run with the new
  `high_motor_optimum_omega` (the maximum over omega of S55-S57).
- Fig. 3(A): `fig3a_tau10` (red, K' = 0.01) over the whole beta_c range; recorded as data only
  (a mean-field run per point, the stiff ones minutes each; see `q_fig3_meanfield`).
- Fig. 3(B): `fig3b_tau10`, `fig3b_tau5`; Fig. 3(D): `fig3d_F2`, `fig3d_F5`; Fig. S4, right:
  `figs4r_tau10`, `figs4r_tau5` - all at beta_c <= 0.15 where K = K'/beta_c >= 6.7. log10 x
  from the long tick at 10^0 and the box lines at 10^-2 and 10^2 (the right line taken where it
  is, since the curves hide the end of the bottom axis); misfits 0.5-2.2 px in x, 1.9-6.0 px in
  y (Fig. S4 has blurred tick marks). Compared with the rigid limit S31-S36 written in
  beta_c (`rigid_clutch_scan`, omega = omega' beta_c as the caption gives) as `approximation`.
  The F = 2 and F = 5 lines of Fig. 3(D) overlap at small beta_c and are told apart by colour.
- Fig. S3: `figs3_F1_tau10`, `figs3_F10_tau10` (the Eq. 6 line for tau = 10 at F = 1 and
  F = 10), read between the symbols from omega = 500; below that the line is too steep to trace.
  The top of the left axis is hidden by the line, so the box's top is taken from the top line.
  The y tick at 0.01 of the F = 10 panel is hidden and that label is not used.
- Fig. S1(B): `figs1b_F025`, `figs1b_F05` (bound fraction for F = 0.25 and 0.5 at K = 0.1-3).
  Run with the mean-field model; together with `q_stall_bistable` this tests which branch the
  paper's lines follow on stiff substrates. The F = 0.5 line sits at n_b* = 0.83, the stalled
  root of S34 (0.829), not the slipping one (0.047): see `q_figs1b_branch`.

## What the readings show

- Fig. 2(C): the Eq. 5 line is drawn with C1 = 0.30, not the printed 0.4 (`q_fig2c_c1`).
- Fig. 2(F): Eq. 6 lies 8-16% below both the mean-field and the stochastic optima read for
  tau = 10 (`q_fig2f_eq6_offset`).
- Figs. 3(B, D), S4: the rigid limit S31-S36 matches the mean-field curves at small beta_c to
  within the reading (e.g. S4 tau = 5: 0.710, 0.660, 0.578, 0.478 against 0.710, 0.658, 0.577,
  0.477).
- Fig. 4(B): tau = 20 traction past its drop and tau = 50 bound fraction agree with S31-S36
  (smallest root) to the third digit.
- Fig. 5(A): F_opt agrees for tau = 10, 20 at small omega but not for tau = 1, 5 at large omega
  (`q_fig5a_fopt`); the inset of 5(B) agrees with the maximum of S55-S57.

## Left out, and why

- Stochastic-model symbols on the lines of Figs. 1(B), 3, 4, 5(B, C), S1, S3, S4: single
  simulations of a model whose code and settings are not given, drawn in the colour of the line
  they sit on and mostly covering it. Only where they stand apart from their line were they read
  (Fig. 2(F) tau = 10). The Fig. 2(C) symbols are the paper's numerical critical activities and
  are read.
- Figs. 1(A), 2(A, B, D, E), 3(C), S2 (p. 23, lower): sketches and time courses (traction,
  bound fraction, densities, extension rate against time) of single loading cycles whose start
  and initial condition are not stated (`q_mf_initial`); no printed number is derived from them.
- Fig. S1(A) (the same F = 10 traction curve as Fig. 1(B), read there) and S1(C) (cycling time:
  no model in the record outputs it); the F = 1, 10, 20 lines of Fig. S1(B) (the mean-field
  solver for them is in the record, but each point is a slow run; the same regime is checked
  through Fig. 1(B)).
- The other tau / F lines of read panels (Figs. 2(F) tau = 0.5, 2, 5 and its other symbols;
  Fig. 3(A, B) tau = 1, 2; Fig. 3(D) F = 1, the same parameters as Fig. 3(B) tau = 10; Figs. 4,
  5(B, C), S3, S4 left): they test the same models at other parameters, and in Fig. 2(F) and
  S3 the lower lines lie within a few pixels of the axis.
- The dashed low-F asymptotes of Fig. 4 (Eqs. S46, S49, S51) and the clutch-extension-rate
  panels of Fig. 4 (right): the asymptotes are not implemented; the v_e* panels need the
  root choice of S34 that the T* and n_b* panels already test.
- Figs. 6, S5, S6 (clutch reinforcement, Eq. 7 / S59-S73) and S7 (catch bond, S86-S88): curves
  of models not in this record (`q_left_out_models`); no measurement is plotted in them.
