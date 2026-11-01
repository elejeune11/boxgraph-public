# Figures of bangasser2013b

## How the figures were read

**Second pass (calibrated, 2026-11-01).** Every plotted curve with values is now read by code from the
PDF at build time. There are 50 readings in `figures.yaml`, each a stub in `figures/` that calls the
shared reader `figures/_fig.py` (pinned by SHA-256). Everything is found in the image:

- **Axes.** The black spines are the longest dark lines of the crop. The tick marks are the short dark
  strokes outside them, and a tick at the other spine is taken as that spine. The ticks are matched in
  order to the printed labels, the only values typed in. A least-squares line (log10 for log axes) is
  the calibration, and its largest residual is the misfit (at least 0.5 px).
- **Curves.** A curve is the set of pixels nearer in colour to its series than to any other series of
  the panel, black or white. The reader traces it column by column and takes the centre of the run.
  Gaps between dashes are bridged by interpolation and widened by half the jump.
- **Vertical strokes.** The abrupt failure of an ODE cycle is read as the rightmost long vertical
  stroke of the series. Its position on the time axis becomes a datum indexed by r.
- **Intervals (95%).** Half the line thickness, the excess of a steep run, the misfit and 1 px; across
  x, the slope times the x misfit.

Main-text panels are vector art, read at 1500 dpi with misfits of 0.5-1.8 px. Supplement panels are
Excel rasters, read at 1200 dpi with misfits of 0.5-9.7 px (q_cal_readings_raster). Every overlay was
checked in `figwork/<reading id>.png`.

The eye-read data of the first pass (`*_ode` with `≈`, q_eye_readings) are kept unchanged. The
calibrated data are `<reading id>_cal`.

## Panel by panel

- **Fig. 2(a)** (p. 6): left out. It is a single stochastic Monte Carlo trajectory.
- **Fig. 2(b)**: read.
  - `fig2b_ode`: blue ODE line at t = 2-25 s.
  - `fig2b_mc`: red dashed Monte Carlo mean, at times that fall on dashes.
  - `fig2b_drop`: the ODE failure, at 28.2 s.
  - Misfit 1.7 px on x, 0.5 px on y.
  - Compared with `run_tc_fig2_cal` and `run_cyc_fig2_drop`. Neither is reproduced (q_cal_tfail_fig2,
    q_cal_ode_curves_fig2).
- **Fig. 2(c)**: read: `fig2c_ode`, `fig2c_mc`, `fig2c_drop` (28.1 s). Misfits 0.5 px.
- **Fig. 2(d)**: read: `fig2d_ode`, `fig2d_mc`, `fig2d_drop` (28.2 s). Misfits 0.5 px.
- **Fig. 2(e)**: read: `fig2e_ode`, `fig2e_mc`, `fig2e_drop`. The stroke is the jump back to vu, at
  28.1 s. Misfits 0.5 px.
- **Fig. 2(f)**: read on the log10 axis: `fig2f_ode` and `fig2f_mc`. The Monte Carlo is also read at
  its peak (27 and 33 s), above the top label. Misfit 0.7 px on x, 1.3 px on y. The ODE off-rate is
  "close" to the run.
- **Fig. 3(a), 3(b)** (p. 7): left out. They are 2D colour-coded histograms, and the colour scale
  cannot be inverted to values at a useful precision.
- **Fig. 3(c)**: read: `fig3c_ode` (blue) and `fig3c_mc` (red), the clutch-force distributions at
  t = 4 s. Misfit 1.2 px. No model of the record outputs the gamma density, so these readings have no
  comparison.
- **Fig. 4(a)**: read: `fig4a_n25` (darkest red, first to rise) and `fig4a_n3600` (dark blue, last).
  These are the Monte Carlo curves at the two labelled ends. They are compared, as approximations, with
  the ODE cycle-mean flow.
  - The five middle curves are left out. The figure labels only the end curves (25 and 3600) and the
    legend does not give the intermediate nm = nc values, so they could not be given conditions.
- **Fig. 4(b)**: read: `fig4b_n25` and `fig4b_n3600`, compared with `run_cyc_fig4b_*`. Misfit 1.3 px
  on x, 0.8 px on y. The middle curves are left out for the same reason as in 4(a). The plotted curves
  support the printed optima of 1 and 200 pN/nm, not the record's runs (q_cal_fig4b).
- **Fig. 5(a), 5(b)** (p. 8): left out. They are 3D surfaces, and a 2D projection cannot be calibrated.
- **Fig. 6(a)**:
  - Top left, ODE: read as `fig6a_ode` and `fig6a_ode_drop` (28.2 s). It is the same cycle as
    Fig. 2(b) and agrees with it.
  - Top right, one Monte Carlo run: left out. It is a single stochastic trajectory.
  - Bottom row, means of 10 and 100 runs: read as `fig6a_mc10` and `fig6a_mc100`. The noise of the
    curve widens the intervals.
- **Fig. 6(b)**: read: `fig6b_ode`, `fig6b_mc1` (lower red line) and `fig6b_mc100` (upper red line,
  traced from a seed on it), on log-log axes. These are run times of the software (origin
  `measured`), with no model. The ODE reads about 0.10-0.12 s, consistent with the 0.11 s of the
  legend.
- **Fig. S1A** (p. 19): left out. It is a single on/off trajectory.
- **Fig. S1B-F**: read: `figS1{b..f}_ode` (blue) and `figS1{b..f}_mc` (red dashed) at t = 1-20 s.
  - S1C labels only 0 and 20 on the time axis.
  - Compared with the single-clutch ODE on the stated 0.1 and the added 0.01 pN/nm, and the ODE
    against the Monte Carlo mean.
  - The S1C plateau (≈200 nm) confirms q_figS1_stiffness, but the transients match neither stiffness
    (q_cal_S1).
- **Fig. S2A, S2B** (p. 20): left out. They come from a single Monte Carlo output: a trajectory, and
  noisy curves derived from it.
- **Fig. S2C**: read: `figS2c_r1`, `figS2c_r2` and `figS2c_r3`, the averaged r Pb Fb - <Fc> of the
  Monte Carlo output. No record model outputs it.
- **Fig. S2D**: read: `figS2d_minr`, the red minimum-r curve on the left axis.
  - The grey actin-flow curve on the right axis is left out. Its axis is grey and runs inside the green
    band, so the black-spine calibration cannot find its ticks. A later pass with a grey-axis
    calibration could read it.
- **Fig. S2E**: read: `figS2e_drops`, the failures for r = 1, 2 and 3 (15.2, 32.1 and 73.4 s), and the
  curves `figS2e_r1`, `figS2e_r2` and `figS2e_r3`. Misfit 9.4 px on x, 9.7 px on y. The r = 1 and r = 3
  drops agree with the printed 15 and 73 s. The r = 2 drop differs from Fig. 2(b): this answers
  q_audit_fig2b_vs_S2E (q_cal_fig2b_vs_S2E).
- **Fig. S2F**: read: `figS2f_r3`, `figS2f_r2`, `figS2f_r1`, `figS2f_r03` and `figS2f_mc`, at 0.1-100
  pN/nm on log-log axes. Misfit 0.5 px on x, 3.6 px on y. This answers q_S2F_stiff (q_cal_S2F). The
  r = 0.3 curve has no run (q_S2F_r03).

## What the calibrated readings settle

- q_eye_readings / q_tcycle_r: the ODE failure in Fig. 2 is at 28.2 s, not the record's 25.7 s
  (q_cal_tfail_fig2).
- q_audit_fig2b_vs_S2E: the difference is real (q_cal_fig2b_vs_S2E).
- q_S2F_stiff: real, and large above 1 pN/nm (q_cal_S2F).
- q_ode_opt_3600: Fig. 4(b) is consistent with the printed 200 pN/nm. The gap is in the record's
  model or its flow average (q_cal_fig4b).
- q_figS1_stiffness: the 200 nm plateau is confirmed (q_cal_S1).
