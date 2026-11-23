# Figures of shen2025

One bullet per figure panel. Readings are in `figures.yaml`; the reading code is
`figures/phase_lib.py` (shared) with one small file per reading, `figures/<id>.py`, that
says which panel and which line (a hash pins the shared file). Check images (magenta
crosses where the code read) are `figwork/<id>.png` (not committed). All readings were
checked with `boxgraph figure check` and the crosses looked at: every cross sits on the
line, curve or marker meant.

**How the readings work** (details in the docstring of `phase_lib.py`):

- **Calibration.** Every panel is a MATLAB axes box with inward ticks. The frame is found
  as the outermost long dark rows and columns. The tick marks are found inside the frame
  on both opposite sides and averaged. Ticks and frame lines are matched in order to the
  printed tick labels: the only numbers typed in. The fit is linear (log10 for Fig. 6).
  The misfit is the largest residual of the marks, at least 0.5 px. It is 0.5-2.8 px at
  1500-1600 dpi; on these axes that is 0.002-0.03 in v~u, 0.002 in w~, 0.03 in nc0.
- **Phase diagrams** (Figs. 2, 5, 6, 13; raster images of coloured regions with black
  boundary lines). In the pixel column of each x, the black runs are the drawn lines. Each
  is classified by the region colour just above and below (S, SS, US, U, N). The run with
  the requested (above, below) pair is read at its centre. The interval is the line's
  half thickness + misfit + 1 px.
- **Curves** (Figs. 8-11). A colour mask is traced column by column from a seed point,
  which only says which curve is meant. Partial runs at the slanted ends of dashes are
  skipped, so dashed and dotted lines bridge. The value is a quadratic fit of the traced
  centres within ±45 px of the column (±110 px for the long dashes of Fig. 11, Nc = 5).
  The interval is misfit + |slope| × x misfit + 2 × fit rms + a quarter of the line
  width + 1 px. A curve lying on the frame line is half hidden, so it is not read there.
- **Markers** (Fig. 12). A red mask is closed and labelled. Each marker's centre is taken
  at its widest rows (its diameter), because curves drawn over a marker hide part of it.
  The interval is widened in proportion to the marker area that is missing.
- **Dropped positions.** The `at` lists keep only the x positions where the line was
  found. Where it was not, the reason is one of these:
  - the boundary does not exist there (it has met the frame or ended);
  - it runs along the frame, or under a white region label;
  - two curves overlap there (Fig. 9(c), Fig. 11(c) at low v~u);
  - the curve lies on the frame line (Fig. 10 at f~s ≥ 6-8).

## Panels

- **Fig. 1 (p. 3), the motor-clutch model on a compliant substrate under load**: left out.
  It is a drawing, with no values.
- **Fig. 2(a) (p. 6), Nc-v~u diagram, ks = kc, γ = Γ**: read.
  - `fig2a_hopf`: SS/US line, the Hopf boundary v~u0(Nc), 12 positions Nc = 1.5-19.5.
  - `fig2a_usu`: US/U line, 12 positions.
  - `fig2a_s_ss`: upper S/SS line, Nc = 1.5-10, until it leaves through the top.
  - `fig2a_wedge_top`, `fig2a_wedge_bottom`: the two edges of the S wedge, Nc = 12-19.5.
  - Misfit 0.5 px (x), 2.4 px (y; the raster's tick spacing varies by ±4 px).
  - Runs: `run_fig2a_hopf` and `run_fig2a_usu` (stability_boundaries, printed A3, sweeping
    Nc). The S/SS and wedge edges have no model in the record. stability_boundaries
    returns only the Hopf and US/U crossings.
  - The reading gives v~u0(10) = 1.635 [1.56, 1.71]. So the caption's point
    (10, 1.7) is just above the boundary, at the edge of the reading's interval
    (`q_vu0_close`).
- **Fig. 2(b), ks = kc, γ = 100 Γ**: read.
  - `fig2b_hopf` (Nc = 1.5-14), `fig2b_usu` (Nc = 1.5-8) and `fig2b_s_ss` (1.5-16).
  - Further right, the US/U line runs into the bottom frame and the Hopf line meets it.
  - Misfit 1.8 / 2.4 px.
  - Runs: printed J55 (`run_fig2b_*`) and corrected J55 (`run_fig2b_*_corr`).
- **Fig. 2(c), matched substrate ks = nc0 kc, γ = Γ**: read.
  - `fig2c_hopf`, `fig2c_usu`, `fig2c_s_ss`, `fig2c_wedge_top`, `fig2c_wedge_bottom`.
  - Misfit 0.5 / 0.5 px.
  - Runs: `stability_matched`, a new model. It is stability_boundaries with k~s = nc0 k~c
    at each Nc, as p. 8 defines the matched substrate.
- **Fig. 2(d), matched substrate, γ = 2 Γ**: read.
  - `fig2d_hopf` (all 12 positions), `fig2d_usu` (Nc ≤ 12, where it leaves the frame)
    and `fig2d_s_ss`.
  - Runs: `stability_matched` with g = 2 (printed J55).
- **Fig. 2(e), ks = 1 pN/nm, γ = Γ**: read.
  - `fig2e_hopf`, `fig2e_usu`, `fig2e_s_ss` (top-left S corner), `fig2e_band_top` and
    `fig2e_band_bottom` (the middle S band).
  - The US/U line is unread at Nc = 2 (under the "U" label) and at Nc ≥ 14 (on the
    frame).
  - Runs: stability_boundaries with `ks_stiff_nd`.
- **Fig. 2(f), ks = 1 pN/nm, γ = 2 Γ**: read.
  - `fig2f_hopf`, `fig2f_usu`, `fig2f_s_ss`, `fig2f_band_top` (a flat line at
    v~u = 11.05) and `fig2f_band_bottom`.
  - Runs: printed and corrected J55.
- **Fig. 3 (p. 7), time courses in the S, SS, US and U states**: left out. These are single
  trajectories at points the paper does not give. Their Nc and v~u are not stated, and the
  initial state and numerics are not stated either. The steady levels in the S and SS
  panels (nm ≈ 1.43, y~ ≈ 9.25) are nm0 and y~0, which do not depend on Nc. They could be
  read as two points, but they add nothing to Figs. 8-10, which plot the same fixed point
  over parameter ranges.
- **Fig. 4 (p. 8), phase portraits nm-x~o and y~-x~o**: left out. Trajectories in the state
  plane, with no stated point or initial state.
- **Fig. 5(a) (p. 9), Nc-w~ diagram, v~u = 15**: read.
  - `fig5a_n_edge`: edge of the N region, Nc = 0.5-7.
  - `fig5a_hopf`: US/SS, Nc = 7.5-11.
  - `fig5a_ss_s`: SS/S, Nc = 3.5-14.5.
  - x calibrated on the frame (0, 15) and ticks 5, 10. y on ticks 0.2-0.8: the bottom
    frame line carries no label. Misfit 0.9 / 1.5 px.
  - No model in the record gives boundaries in w~, so there are no runs.
  - The N edge read in 5(a) and 5(b) agrees to 0.001 at every Nc. That fits the
    saddle-node condition w~max(Nc, F~), which does not involve v~u.
- **Fig. 5(b), v~u = 5**: read.
  - `fig5b_n_edge`, `fig5b_u_us`, `fig5b_hopf` and `fig5b_ss_s` (Nc = 2-6, where SS/S
    meets the bottom).
  - No runs.
- **Fig. 6(a) (p. 9), k~s-k~c diagram, Nc = 15, v~u = 15, log-log**: read.
  - `fig6a_band_top`, `fig6a_band_bottom`: the SS band at left, k~s = 0.015-0.9.
  - `fig6a_right_top`, `fig6a_right_bottom`: the SS region at right.
  - Calibrated on decade ticks: the long ticks only, since the minor ticks are shorter.
    Misfit 1.1 / 1.5 px, i.e. 0.002-0.003 decade.
  - The near-vertical parts of the boundaries at k~s ≈ 1-5 are not read, because a
    column reading is meaningless there.
  - No runs: the record's models give boundaries in v~u, not in k~c.
- **Fig. 6(b), Nc = 10, v~u = 1.7**: read.
  - `fig6b_hopf` (SS/US), `fig6b_usu` (US/U) and `fig6b_right_top`.
  - No runs.
- **Fig. 7(a,b) (p. 9), Γ-γ diagrams**: left out, for three reasons:
  - The y axis has one labelled interior tick (10^-4) plus the labelled top frame line
    (10^-2). The bottom is unlabelled, among minor ticks, so a calibration would rest on
    two marks with no check.
  - The boundaries fold back: the SS/S and US/U lines are not single-valued in Γ over
    much of the panel.
  - Γ also sets every characteristic scale (l0, τ, v0, f), so no model in the record
    takes Γ as an input (source notes).
- **Fig. 8(a-f) (p. 10), nc0 against Nc, Nm, w~, k~off/k~on, F~b, f~d**: read, 11 curves.
  - Ids `fig8{a..f}_Nc{10,20}`; panel (a) has only Nc = 20 (one curve).
  - The light blue (Nc = 10) and dark blue (Nc = 20) curves are told apart by colour. The
    solid and dashed parts of one curve are read as one curve.
  - Misfit 1.0-1.7 px.
  - Runs: fixed_point, sweeping Nc, Nm, w~, F~b or f~d.
  - Panel (d)'s x axis is the ratio k~off/k~on, a new quantity `clutch_rate_ratio_nd`.
    The model takes k~off and k~on separately, so (d) is read but not run.
- **Fig. 9(a-f) (p. 10), x~o0 against the same parameters**: read, 11 curves,
  `fig9{a..f}_Nc{10,20}`.
  - Runs: fixed_point with ks = kc (soft substrate).
  - Not read: Fig. 9(c) Nc = 10 at w~ = 0.05, where the light curve is under the dark one.
    Fig. 9(f) at f~d = 0.5, on the near-vertical rise.
- **Fig. 10(a-f) (p. 10), nm0, nc0, x~o0, y~0, x~s0, x~c0 against f~s at Nc = 20**: read,
  `fig10a`-`fig10f`.
  - Runs: fixed_point sweeping f~s.
  - Not read: f~s ≥ 6 in (a), and ≥ 8 in (c, e, f), where the curve lies on the bottom
    frame line.
- **Fig. 11(a,b) (p. 11), heat maps of frequency and amplitude over (Nc, v~u)**: left out.
  - A colour-scale reading would need the colour bar mapped through a nonlinear colormap
    on a raster.
  - Panels (c, d) give the same quantities as line profiles, read below.
- **Fig. 11(c), frequency against v~u at Nc = 5, 10, 15**: read, `fig11c_Nc5`,
  `fig11c_Nc10` and `fig11c_Nc15` (blue dashed, red dashed, yellow dotted).
  - x calibrated on the ticks 1 and 1.5: the frame edges are not at labelled values.
  - Runs: limit_cycle sweeping v~u, Fig. 2(a) conditions.
  - Not read: at v~u ≤ 1.3 the three curves overlap, and only the topmost is visible.
- **Fig. 11(d), amplitude of y~ against v~u**: read, `fig11d_Nc5`, `fig11d_Nc10` and
  `fig11d_Nc15`.
  - Runs: limit_cycle (amplitude = half the peak-to-peak range, as the record's model
    defines it) and limit_cycle_ptp (amplitude = peak-to-peak), a new model on the same
    integration.
  - The near-vertical ends at the Hopf points are not read.
- **Fig. 12 (p. 12), nc0 against Nc for ten loads, with the saddle-node points**: read,
  `fig12_points`, the ten red points.
  - Calibration misfit 0.5 px.
  - Run: saddle_locus, a new model. From Eqs. 16-17 the saddle-node condition
    g'(nc0) = 0 fixes u = (nm0 f~s - F~)/(nc0 F~b) whatever the load. So all saddle-node
    points lie on the line nc0 = Nc,min/(1 + (k~off0/k~on) e^u), the black arrow of the
    figure. The run sweeps Nc over the points' read x positions.
  - The ten solid and dashed branches are not read. They are ten nearly parallel
    coloured curves that cross and overlap near the origin. The points carry the
    paper's result (Nc,min against load), and run_saddle_F0 already covers the j = 0
    branch end.
- **Fig. 13(a) (p. 12), Nc-v~u at F~ = (1/2) nm0 f~s**: read, `fig13a_hopf`, `fig13a_usu`
  and `fig13a_s_ss`.
  - Runs: stability_boundaries with F~ from a new processing model `load_of_fraction`
    (F~ = load × nm0 f~s) and the datum `loadfrac_half`.
- **Fig. 13(b), F~ = nm0 f~s**: read, `fig13b_hopf`, `fig13b_usu` and `fig13b_s_ss`.
  - No runs: at F~ = nm0 f~s the record's models raise (A = 0; `q_case2_trivial`).
- **Fig. 13(c-f), Nc-w~ at F~ = (1/2) F~(w~=1) and F~(w~=1)**: read.
  - `fig13c_{n_edge,hopf,ss_s}`, `fig13d_{n_edge,u_us,hopf,ss_s}`,
    `fig13e_{hopf,ss_s}` and `fig13f_{u_us,hopf,ss_s}`.
  - The small N and U corners of (e) and (f) are not read; they are a few columns wide.
  - No runs (boundaries in w~).

No figure in this paper plots measured data: there are no points with error bars, bars or
histograms. Every plot is a model result.

## What the comparisons show

These were checked before the build, by running the record's models at the read positions
against the reading intervals. The build computes the verdicts.

- **Fig. 2 Hopf and US/U boundaries, printed A3.** All read points lie within the reading
  intervals: panels (a), (b), (e), (f) with stability_boundaries, and (c), (d) with
  stability_matched. So the paper's diagrams follow from its own Jacobian A3 and Table II.
- **J55 corrected** (`cmp_fig2b_*_corr`, `cmp_fig2f_*_corr`):
  - Fig. 2(b) cannot tell the two forms apart.
  - Fig. 2(f) can. The corrected Hopf boundary leaves the reading from Nc = 10 on, by up
    to 0.34 in v~u at Nc = 18, against an interval of ±0.05.
  - So the γ ≠ Γ diagrams use J55 as printed (new question `q_fig2_settles_J55`, on
    `q_A3_J55`).
- **Figs. 8, 9, 10 (fixed points).** The readings agree with Eqs. 9-15. x~o0 and x~s0 need
  ks = kc (`q_fig9_ks_kc`, on `q_ks_figs8to10`). Fig. 10(b)'s narrow axis (18.0-18.2)
  makes the nc0 check sharp: the readings agree to about 0.001.
- **Fig. 11(c).** The frequencies agree with limit_cycle, with τ = 1/ωd0.
- **Fig. 11(d).** The amplitudes are twice the record's half-range and equal to the
  peak-to-peak range (`q_fig11_amplitude_ptp`, on `q_amplitude_def`). The text layer's
  "proportional to v~u0 - v~u" has lost a square root that the page prints
  (`q_amplitude_sqrt_printed`, on `q_amplitude_linear`).
- **Fig. 12.** All ten saddle-node points lie on the locus of Eqs. 16-17. Their x positions
  fall by about 0.098 per load step, i.e. Nc,min is proportional to (1 - j/10). This is
  as the locus implies, with nc0 proportional to nm0 f~s - F~.
- **Fig. 13(a).** At F~ = (1/2) nm0 f~s the stability_boundaries run agrees at all read
  points.
- **Fig. 13(b).** At F~ = nm0 f~s it shows the same boundaries, so a fixed point exists at
  A = 0 (`q_fig13b_fixed_point`, on `q_case2_trivial`).
- **Fig. 2(a) and `q_vu0_close`.** The Hopf boundary at Nc = 10 reads 1.635 [1.56, 1.71].
  The caption's "close to the boundary" point v~u = 1.7 is inside the SS region, at the
  edge of that interval.
