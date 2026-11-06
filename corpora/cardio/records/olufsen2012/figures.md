# Figures in olufsen2012

Every figure that has values was read with the record's own code (`mode: code`). The code is in `figures/`:
- `_common.py`: frame detection, tick-label calibration, colour masks and line fits.
- `_fig5.py`: Fig. 5.
- `_fig89.py`: Figs. 8 and 9.
- `_wave.py`: Figs. 3, 6, 7, 10, 11 and 13.

Each reading has a one-line file `figures/<reading id>.py`.

Calibration works the same way for every panel. The plot box is found as the frame of long dark lines. The printed tick
labels are found as clusters of ink left of the box and under it: each label's centre is its tick's row or column. A
straight line, value to pixel, is fitted to the labels I matched, and its worst misfit is added to every interval. Where
a lone "0" sits under the lower-left corner, it could belong to either axis, so it is left out (`x_skip`, `y_stop`). The
misfits quoted below are the worst label misfits, in pixels of the rendered crop.

An earlier version cut off the labels at both ends of the x axis. That gave x misfits of 14-20 px on Fig. 8(c) and
Fig. 9 (right). The label band is now three margins wider, and ink touching its top edge is ignored. Every Fig. 8/9
misfit is now at most about 3 px.

Every reading was checked with `boxgraph figure check`, and the overlays in `figwork/` were inspected.

## Read

- **Fig. 3(a)** (p. 8): `fig3a_aorta`. The measured aortic inflow, dark-blue curve, read at t = 0.05-1.05 s in steps
  of 0.05 s. Origin: measured. Calibrated on x labels 0.2-1.0 and y labels -100 to 500; misfit x 4.7 px, y 0.8 px at
  1500 dpi. No model in the record predicts it; it is the input of the non-runnable network.
- **Fig. 3(b)** (p. 8): `fig3b_pulm`. The measured main pulmonary artery inflow, blue curve, t = 0.025-0.675 s.
  Origin: measured. Misfit x 3.7 px, y 0.3 px.
- **Fig. 5** (p. 10): four readings on a soft raster image at 1200 dpi. Calibrated on the labels -5 to 1 and -2 to 4
  plus the frame lines; misfit y 2.7 px, x 17 px (the raster labels are unevenly placed).
  - `fig5_points_large`: the 9 blue diamonds, Huang et al. data, origin measured. The error bars are read where a cap
    shows outside the marker (log(r) of about 0.3 and 0.76; one upper cap at -0.12, whose lower cap is taken as its
    mirror). Elsewhere a bar is at most the marker. The paper does not say what the bars are (`unstated`).
  - `fig5_points_small`: the 4 red squares, origin measured.
  - `fig5_line_large`: the solid least-squares line, read between the markers.
  - `fig5_line_small`: the dashed least-squares line, read between the red markers.

  Model `length_radius_loglinear_fig5` (log(l) = a log(r) + b) is swept over each reading. The solid line's label
  reproduces the drawn line (cmp_fig5_line_large) and fits the blue points (cmp_fig5_points_large). Eq. 2.19 also fits
  the blue points (cmp_eq219_points_large). The dashed label, slope 0.04733, reproduces neither the drawn dashed line
  nor the red points: the drawn slope is about 0.47. This settles the doubt in q_fig5_small_slope in favour of a lost
  digit; see q_fig5_dashed_line_drawn. There are 13 markers, not the 15 orders of the text: see q_fig5_point_count.
- **Fig. 6(a)** (p. 16): `fig6a_aorta` and `fig6a_pulm`. The simulated flows in the aorta and the main pulmonary
  artery, single blue curves, read at the same times as Fig. 3. Misfit x 4.4 / 0.2 px, y 0.6 / 0.4 px. They are
  compared with Fig. 3 in cmp_inflow_fig6a_fig3_aorta and cmp_inflow_fig6a_fig3_pulm, and they differ: see
  q_fig6a_vs_fig3.
- **Fig. 7(a)** (p. 17): `fig7a_aorta` and `fig7a_pulm`. The simulated pressure in the aorta (t = 0.05-1.05 s) and in
  the main pulmonary artery (t = 0.05-0.65 s), blue curves. Misfit x 4.9 / 0.5 px, y 0.7 / 0.0 px. Origin predicted;
  produced by the non-runnable network.
- **Fig. 7(d)** (p. 17): mean pressure against log10 of radius (um).
  - `fig7d_sys_centre` and `fig7d_pulm_centre`: the red centre lines, read where they are smooth (log10 r = 2.25-3.0
    systemic, 2.1-2.9 pulmonary).
  - `fig7d_*_beta`: the blue lower lines.
  - `fig7d_*_alpha`: the green dashed upper lines, read with a 40-column window that spans the dash gaps.

  Calibrated on labels 4 to 0 and the pressure labels; misfit x 1.2 px, y 0.7 / 0.6 px. Model
  `pressure_log_radius_eq31` (Eq. 3.1) is swept over the centre lines as a fit_quality check. The systemic relation lies
  near its line. The pulmonary relation, 14 log10 r - 25, is far from its line: see q_eq31_pulm_fit, which bears on
  q_eq31_scope.
- **Fig. 8(a)** (p. 18): `fig8a_g025`, `fig8a_g05`, `fig8a_g075`, `fig8a_g1`. Area ratio eta against xi for
  gamma = 0.25 (blue dotted), 0.5 (green dashed), 0.75 (red dash-dot) and 1.0 (cyan solid), at 1800 dpi. Read at the
  computed points xi = 2.4, 2.6, 2.8, where the drawn straight segments meet: a line is fitted on each side of the
  point and the two are intersected. Misfit x 2.5 px, y 0.9 px. Intervals are about +-0.002.

  Eq. 2.18, right-hand form (`area_ratio_eq218`), reproduces all twelve values. The left-hand form with gamma = r_d1/r_d2
  (`area_ratio_eq216_217`) does not, except at gamma = 1. This bears on q_gamma_definition; see q_fig8a_gamma_form.
- **Fig. 8(b)** (p. 18): `fig8b_*`. Total vessel count against xi, four gamma curves at xi = 2.4, 2.6, 2.8.
  Misfit x 2.2 px, y 3.6 px. No runnable model: the tree's root radius is not stated (q_tree_counts).
- **Fig. 8(c)** (p. 18): `fig8c_*`. Vessel count against eta, read at eta = 1.10-1.24 (blue up to 1.165, where it ends).
  Misfit x 2.8 px, y 0.0 px. The curves extend past the eta that Fig. 8(a) gives at xi = 3: see q_fig8c_extra_points.
- **Fig. 9, left** (p. 18): `fig9a_*`. End-branch count against xi at xi = 2.4, 2.6, 2.8. Misfit x 1.6 px, y 0.5 px.
- **Fig. 9, right** (p. 18): `fig9b_*`. End-branch count against eta. Misfit x 1.6 px, y 5.0 px. Same remark as for
  Fig. 8(c).
- **Fig. 10** (p. 19): `fig10_<gamma>_xi<xi>`, 20 readings: four gamma panels, each with five xi curves (2.2 blue solid,
  2.4 green dotted, 2.6 red dashed, 2.8 cyan dash-dot, 3.0 purple dash-dot-dot). Femoral flow, read at t = 0.35-0.55 s,
  where the five curves are apart. Misfit x 4.3-7.4 px, y 1.1 px at 1200 dpi. Produced by the non-runnable network.
- **Fig. 11** (p. 20): `fig11_<gamma>_xi<xi>`, 20 readings. Main pulmonary artery pressure, read at t = 0.3-0.6 s.
  Calibrated on x labels 0.2-0.6 and y labels 0-40; misfit at most 0.4 px. The table that summarises these runs
  (Table 2, PuA rows) does not say which gamma it used. By eye, the xi = 2.2, 2.6 and 3.0 curves of the gamma = 0.5 panel
  have means and swings close to 33/3, 10/12 and 5/12 mmHg. These readings bear on q_table2_trend_claims (pulmonary
  pulse pressure flat from xi = 3.0 to 2.6, then falling). A model input is a scalar, so the record cannot turn a read
  waveform into a mean and a pulse pressure.
- **Fig. 13, rows 3 and 4** (p. 22): `fig13p_<col>_<mean|peak|trough|pulse>` and `fig13q_<col>_<mean|peak|trough>`,
  21 readings. Mean, peak, trough and pulse pressure, and mean, peak and trough flow, in the proximal aorta (a), the
  radial artery (b) and the main pulmonary artery (c), against the % change in large-vessel stiffness. Read at -45 to
  95 %; column (c) only right of its legend (30-95 %). Misfit x at most 12 px, y at most 0.6 px (column (c) and
  Fig. 13(b) row 4 are calibrated without the corner "0" label). Within the readings, pulse is close to peak minus
  trough: at 0 %, 117.9 - 86.3 = 31.6 against 30.9 in the aorta.

## Left out

- **Figs. 1, 2, 4** (pp. 3, 5, 9): drawings (network schematic, tapering vessel, structured tree); no values.
- **Fig. 6(b,c)** (p. 16): flow along the alpha- and beta-branches. Dozens of same-colour curves, one per generation;
  the curves cannot be told apart, and which generation each one is is not given.
- **Fig. 6(d)** (p. 16): mean flow along the branches. The dashed and solid lines coincide within the line width over
  almost the whole range (both near 0 below log10 r = 3).
- **Fig. 7(b,c)** (p. 17): pressure along the alpha- and beta-branches. Same-colour curves per generation, which cannot
  be told apart.
- **Fig. 12** (p. 21): radial-artery flow for seven compliance changes. The seven thick curves are drawn over one
  another and coincide within their line width except near the first peak, where they are stacked and partly hidden.
- **Fig. 13, rows 1 and 2** (p. 22): pressure and flow waveforms for seven stiffness changes. Seven thin dashed
  curves in close colours cross repeatedly. Their peak, trough and mean are what rows 3 and 4 plot, and those rows are
  read.
