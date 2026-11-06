# Figures of reymond2009

Every figure that plots values is read by the record's own code (`figures/`, `mode: code`). Each build renders the
crop again and reads it. Every reading was checked with `boxgraph figure check`, and the marks sit on the curve or
point meant. The first pass read no figure, so there were no eye-read values to keep.

- **Fig. 1A** (p. 4): a schematic pressure-volume loop with no axis values. Left out.
- **Fig. 1B** (p. 4), read at 1400 dpi. Two readings:
  - `fig1b_EN_measured`: the gray line "EN measured", Senzaki et al.'s normalized elastance (ref. 54), at tN 0.05-2.95.
    Datum `EN_measured_fig1b`, origin measured, from_source ref-54.
  - `fig1b_EN_isovolumic`: the black line "E*N isovolumic", at tN 0.40-0.95. Elsewhere it lies under the gray line.
    Datum `EN_isovolumic_fig1b`, origin derived.

  Calibration: the axis lines and the single labelled tick on each axis (1), with y = 0 at the x axis and tN = 0 at
  the y axis (two marks, no misfit to measure; q_fig1b_origin). No model in the record takes them: E*N is an
  unprinted input of the non-runnable 1-D model (q_1d_not_runnable). This reading now supplies that input as a curve.
- **Fig. 2** (p. 5): a drawing of the tree topology, with no values. Left out.
- **Fig. 3** (p. 7), read at 1200 dpi. The x ticks 0-30 mm (7) and y ticks 5-15 m/s (6) were found in the image and
  fitted linearly, misfit at most 0.5 px on both axes. The y axis is broken below 5. The x axis lies at 3.0 on the
  fitted scale, so the scale is taken as continuous, and the one point below 5 says so.
  - `fig3_points`: the 16 literature markers (diamond centroids; GA, HA, LA, LU, MU, BA). Their SD bars are read
    where they can be: four bars with both ends capped, the small bar at d ≈ 19.4 mm, and the [BA] bar at d ≈ 15 mm,
    taken as symmetric because its lower end runs into the [LA] marker. The bars at d ≈ 29 mm share one stem and are
    not read (q_fig3_shared_bars). Datum `pwv_lit_fig3`, origin measured.
  - `fig3_fit`: the drawn power-law curve at d = 1-28 mm (markers, error-bar stems and text masked out). Datum
    `pwv_fit_fig3`, origin predicted.

  New model `pwv_eq22` (Eq. 22) is swept over both readings:
  - `cmp_pwv_eq22_fig3_fit` (reproduction): the drawn curve is reproduced within the rounding of the printed a2 =
    13.3 and b2 = 0.3. It lies a little above 13.3/d^0.3 at large d, as an unrounded exponent near 0.29 would.
  - `cmp_pwv_eq22_fig3_points` (fit_quality): Eq. 22 against the literature points; some points agree within their
    reading or SD interval and others do not, in line with the printed R2 = 0.6.

  **The figure settles q_eq22_units**: Fig. 3 plots PWV in m/s against diameter in mm, and its curve is Eq. 22 with
  a2 = 13.3, b2 = 0.3 in those units.
- **Fig. 4** (p. 8), panels A-F, read at 1800 dpi. Each panel has two readings:
  - `fig4X_f_vivo` / `fig4f_p_vivo`: the top sub-panel's thick line, the volunteers' averaged waveform. Datum
    `wave4X_..._vivo_fig`, origin measured.
  - `fig4X_f_model` / `fig4f_p_model`: the bottom sub-panel's model line. Datum `wave4X_..._model_fig`, origin
    predicted.

  Each sub-panel's y axis has two labelled ticks: 0/500, 0/300, 0/150, 0/50, 0/25 ml/s, and 80/120 mmHg in F.
  These are found in the image (two marks; 1 px allowed). Time is measured from the left end of the panel's 0.8 s
  scale bar (q_fig_time_origin) and read every 0.02 s where the line is drawn. The thick line is isolated from the
  thin individual lines by a morphological opening. Where thin lines merge into it, the interval widens.

  The read extremes agree with Table 4's systolic flows (in vivo and model) and with Table 5's radial in vivo
  pressures. The radial model wave peaks at the 120 tick, while Table 5 prints 125 (q_fig_model_pressure_vs_table5).
  The individual volunteers' thin lines are not read: they cannot be told apart, and the paper does not identify
  them.
- **Fig. 5** (p. 10), panels A-F, read at 1800 dpi in the same way: `fig5X_f_vivo` / `fig5X_p_vivo` and
  `fig5X_f_model` / `fig5X_p_model`, with data `wave5X_..._fig`. Tick labels: MCA 2/4, temporal 80/120, VA 1/3,
  ICA 2/10, CCA flow 0/20, CCA pressure 80/120.
  - The flow extremes agree with Table 4.
  - The temporal model wave is lower than Table 5 at both systole and diastole (q_fig_model_pressure_vs_table5).
  - The averaged in vivo CCA pressure of Fig. 5F stays between the 80 and 120 ticks, against Table 5's 101/68 mmHg
    (q_fig5f_vivo_vs_table5). Its extremes resemble the model's tabulated 115/81 instead.

  The thin lines are not read, as in Fig. 4.
- **Fig. 6** (p. 11), panels A and B, flow and pressure, read at 1500 dpi. This is a raster image. In each panel the
  gray line is "With cerebral arterial tree" (the present model) and the dark line is "Without cerebral arterial tree"
  (the Stergiopulos et al. model, ref. 64), as the leader lines show. Readings `fig6X_f_with`, `fig6X_f_without`,
  `fig6X_p_with`, `fig6X_p_without`; data `wave6X_..._fig6`, origin predicted. Tick labels: 0/30 and 0/200 ml/s,
  80/120 mmHg.
  - The lines are separated by gray level and traced by continuity, with leader lines passed over.
  - Where one line is drawn under the other, it is read on the covering line's run with a widened interval.
  - At t of about 0.42-0.46 s in 6B (flow), the dark line is not read: a leader line joins it there.

  No model in the record can produce these curves (q_1d_not_runnable).

None of the waveforms (Figs. 4-6) is compared with a run: the 1-D model is not runnable. The in vivo averaged
waveforms are recorded as measurements for other papers' models to be validated against. The model and in vivo lines
are not compared with each other point by point because their relative time alignment is not stated
(q_fig_time_origin).
