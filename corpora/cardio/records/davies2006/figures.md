# Figures of davies2006

The first reading read no figure (q_figures_not_read). This pass (2026-11-10) reads every figure that plots data,
with calibrated code that every build runs on the page itself (`figures.yaml`, code in `figures/`). Every reading
is a measurement (origin `measured`). No figure has error bars. Shared code:

- `figures/_scatter.py` (Figs. 6 and 7). These are spreadsheet charts embedded as low-resolution rasters; at
  1200 dpi one image pixel is 8 px. The axes are the grey lines. The ticks are faint grey runs outside the axes,
  matched to the printed labels with a straight-line fit (one label may have no tick found). Markers are black
  ink opened with a disk of a quarter of the marker diameter, which removes the regression line and the r/p text.
  Fused markers are counted by area, or by length measured with the regression line's band blanked, and split by
  k-means. Each marker's interval is one image pixel plus the misfit (a quarter marker diameter for a split one).
- `figures/_traces.py` (Figs. 3, 4 and 5). Each recording is one crop holding all its panels. The y axes are
  the long vertical axis lines, with ticks found inside them. The time axis is that of the bottom
  (pressure/velocity) panel. The WI panels have none of their own; the grey onset lines drawn straight through
  all panels show that the panels share it (q_figures_read). WI+ is the top edge of the trace and WI- the bottom
  edge, because acceleration waves are filled; the trace is every ink component reaching the zero row. Pressure
  is the solid line: its long dark components chained end to end and traced column by column. Velocity is the
  dashed line, followed dash to dash, with gaps bridged and fused runs where it crosses the pressure line.
  Extrema readings (`*_peaks`) are the local extrema of the traced WI line with a prominence above 0.1 x 10^5
  W m^-2 s^-2.

Each reading was checked with `boxgraph figure check` and its overlay inspected (`figwork/<id>.png`): the
magenta marks sit on the intended curve or marker.

## Per panel

- **Fig. 1, Fig. 2 (p. 4), Fig. 8 (p. 9)**: left out. They are schematic drawings of wave origin and direction,
  with no values.
- **Fig. 3, upper panel (p. 5), WI+, circumflex**: read. `fig3_wi_plus` is the top edge every 10 ms from 20 to
  930 ms. `fig3_wi_plus_peaks` holds the six maxima: the unlabelled early peak, waves 2, 4 and 6, a mid-systolic
  hump near 250 ms and a small diastolic one near 620 ms. y is calibrated on the ticks 0 to 2 (x 10^5), misfit 1.8 px; x on the bottom panel's ticks 0 to
  1000 ms, misfit 2.7 px. One image pixel is about 0.01 x 10^5 here, so intervals are ±1500 W m^-2 s^-2 or more,
  and wider on steep flanks. Data `fig3_wi_plus_trace` and `fig3_wi_plus_peak_values`.
- **Fig. 3, middle panel, WI-**: read the same way (bottom edge). `fig3_wi_minus` and `fig3_wi_minus_peaks`
  hold waves 1, 3 and 5, a mid-systolic dip and the post-5 trough. Ticks 0 to -2, misfit 1.9 px.
- **Fig. 3, lower panel, pressure (solid, right axis 80-140 mmHg) and velocity (dashed, left axis 0.05-0.3
  m/s)**: read every 10 ms from 20 to 930 ms (`fig3_pressure`, `fig3_velocity`). Misfits are 2.7 and 3.1 px.
  The "velocity" and "pressure" labels are blanked. Velocity is fused with the pressure line at 130 and 150 ms
  (the interval spans the joint run) and is bridged across dash gaps elsewhere.
- **Fig. 4 (p. 6), three panels (circumflex, LAD, left main stem) of one subject, WI+ and WI- in one boxed
  panel**: read as WI+ and WI- traces every 10 ms from 50 to 900 ms, plus their extrema (`fig4cx_*`, `fig4lad_*`,
  `fig4lms_*`, 12 readings). This is a blurred scan. Frame lines are 16 px wide, and ticks are searched 3-20 px
  inside the frame. Misfits are 1.4-8.8 px; the left main stem panel's y axis is the worst. Before 50 ms the trace lies
  within 6 frame widths of the left frame and is not read. The circumflex panel's wave 2 touches the top frame
  and is not read there: 130 ms is left out of `fig4cx_wi_plus`, and its maximum is not among the extrema of
  `fig4cx_wi_plus_peaks` (an extremum at a frame may be clipped). The circumflex panel repeats Fig. 3's
  recording (q_fig3_fig4_same_recording).
  - **Fig. 4 pressure and velocity boxes**: left out. In this scan the dotted velocity line prints as a nearly
    continuous line, in places darker than the solid pressure line. The two cross three times per panel, and the
    code could not keep them apart: a trial reading followed the wrong line after the crossings. The circumflex
    pressure and velocity are read in Fig. 3, which appears to be the same recording.
- **Fig. 5 (p. 7), LVH subject (septum 1.6 cm), circumflex**: read like Fig. 3 (`fig5_wi_plus`,
  `fig5_wi_plus_peaks`, `fig5_wi_minus`, `fig5_wi_minus_peaks`, `fig5_pressure`, `fig5_velocity`), every 10 ms
  from 20 to 840 ms. The ticks are WI+ 0 to 6, WI- 0 to -2, velocity 0 to 0.4 m/s, pressure 70 to 120 mmHg, and
  time 0 to 900 ms; misfits are 0-4.4 px. The circled labels 1 and 5 touch the tips of their WI- troughs and are
  blanked below the tips. The panel title inside the bottom panel is blanked. The solid line breaks where it is
  steep (110 ms, the incisura near 410 ms); the pieces are chained, and one 10 ms point is bridged. Data carry
  `subject_group: LVH`.
- **Fig. 6 (p. 8), backward suction wave % against LV septum (cm)**: read, every marker (`fig6_points`, 20
  markers). Two near-coincident pairs at 1.1 and 1.5 cm are split. y is calibrated on ticks 0-45, misfit 3.4 px;
  x on 0-2 cm, misfit 0.4 px. The regression line is not read. Ten markers lie at 1.1 cm or less and ten at
  1.3 cm or more, which agrees with n_lvh = 10. The group means could check 33.1% / 26.9% and the septum means,
  but the record cannot form a mean of a curve (q_fig6_groups). Datum `fig6_suction_vs_septum`.
- **Fig. 7 (p. 8), forward suction wave % against "Age (years)"**: read, every marker (`fig7_points`, 20
  markers, two fused pairs near 19 and 21 split). Ticks are y 0-80 and x 0-30; misfits are 2.7 and 1.6 px. The calibrated reading confirms q_fig7_axes: every marker lies between the
  10 and 30 ticks and above 30%. A possible reading is that the x axis is coronary wave speed (q_fig7_reading).
  Datum `fig7_fsuction_vs_age`, on the axis as labelled.

- **Fig. 3 and Fig. 5 lower panels, 2 ms readings (added 2026-11-11)**: `fig3_pressure_2ms`, `fig3_velocity_2ms`,
  `fig5_pressure_2ms`, `fig5_velocity_2ms` read the same lines with the same code every 2 ms (20-930 ms and
  20-840 ms). Calibration and misfits are those of the 10 ms readings (2.6-3.8 px). The overlays sit on the solid
  and dashed lines. At this grid the read lines move in steps of one raster pixel (about 0.17 mmHg, 0.002-0.003
  m/s). These readings serve the reading-grid refinement (q_wia_grid). Data `*_trace_2ms`.

## Runs and comparisons with curve ports (2026-11-11)

Curve ports let a model take a read trace whole. With them:

- **Wave intensity analysis rebuilt** (`wia_traces`, runs `run_wia_fig3*`, `run_wia_fig5*`). Pressure and velocity
  of Figs. 3 and 5 give the single-point c (25.4 and 14.8 m/s), separated P+-, U+-, and WI+ and WI- resampled onto
  the read WI traces' x. These are compared point by point with `fig3_/fig5_wi_plus_trace` and `wi_minus_trace`,
  and at the read extrema with the `*_peak_values`. The comparisons are mostly close but not reproduced; see
  q_wia_rebuilt. It is run with no filter and with an added 50 ms Savitzky-Golay window. `run_c_fig3/5` runs the
  printed single-point equation on the model's sums.
- **Reading grid** (q_wia_grid): refinements `ref_grid_*` over the step (10, 4, 2 ms) on the 2 ms readings. The
  peaks do not settle. The 10 ms grid smooths the narrowest peaks by about 20-35%, and finer steps amplify the
  raster's one-pixel staircase.
- **Cumulative intensity and shares** (`cumulative_wi_curve`, `run_cum_*`). These are computed from the plotted WI
  traces and from the rebuilt ones, with the six waves' sum or the whole cycle as total, and compared with Table 2
  as a one-subject consistency check (q_cumulative_rebuilt). Wave 4 of the rebuild is much smaller than plotted
  (q_wave4_rebuilt_small).
- **Fig. 6 group statistics and Fig. 7 correlation** (`scatter_group_stats`, `scatter_correlation_fig7`). The read
  markers reproduce 33.1% / 26.9%, the septum means 0.94 / 1.4 cm, n = 10 LVH, r = -0.52 and, for Fig. 7, r = 0.64
  (q_fig6_groups_run, which answers q_fig6_groups).
- **Diastolic-to-systolic velocity ratio** (`diastolic_systolic_velocity_ratio`, `run_dsr_*`). This is computed for
  the yong2025 test, with end-systole added and run both ways. No validation is entered (q_yong2025_dsfr).
- Fig. 4 is still not used in a run: its pressure and velocity are not read, and its Cx wave 2 is clipped by the
  frame.

## Runs, comparisons and open questions (first figure pass, 2026-11-10; kept as written)

No run or comparison is added. No model in this record can take a figure curve. A model port takes a number,
and a sweep passes only a curve's time index, so neither the wave intensity analysis (q_fig_traces_not_run) nor
the group means of Fig. 6 (q_fig6_groups) can be formed. The traces are single subjects, while Table 2 holds
cohort means.

These readings can serve later validations, but they are not forced here. A human left coronary pressure and
velocity time course at rest (Fig. 3) and in LVH (Fig. 5), and WI+ and WI- in the LMS, LAD and Cx of one
subject (Fig. 4), are what a coronary model in the corpus (yong2025, kim2010, mynard2015) would be compared
against. A velocity comparison still needs the added vessel diameter and the Doppler-peak-to-mean factor of
q_validation_candidates.

Questions answered or sharpened by the figures:

- q_figures_read answers q_figures_not_read.
- q_fig3_signs settles the figure side of q_table2_sign.
- q_fig7_reading confirms q_fig7_axes.
- q_fig3_fig4_same_recording notes that Fig. 3 and Fig. 4's circumflex panel are one recording.

The existing eye-read data are kept unchanged.

Questions added by the curve-port pass: q_wia_rebuilt (answers q_wia_not_run), q_cumulative_rebuilt (answers
q_cumulative_not_runnable), q_fig_traces_run (answers q_fig_traces_not_run), q_wia_grid, q_wave4_rebuilt_small,
q_fig6_groups_run (answers q_fig6_groups and supports q_fig7_reading), and q_yong2025_dsfr.
