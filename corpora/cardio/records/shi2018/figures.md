# Figures of shi2018

Every plot in the paper's pages 2-8 is listed, panel by panel. Fig. 5 is read by code
(`figures/_fig5.py`, shared by all readings, and one small `figures/<reading>.py` per reading),
each panel rendered at 900 dpi.

**Calibration (all Fig. 5 panels).** The axes are the column and row with the most ink. Tick
candidates are runs of ink leaving the axes; the labelled ticks are the longer ones forming the
longest evenly spaced chain, matched in order to the printed labels (and the corner to 0 in (a) and
(d)). A straight line is fitted per axis. The figure is a low-resolution raster (about 150 dpi:
lines come in 6 px steps at 900 dpi), so the fit misfits are 2-4 px at 900 dpi (y / x): (a) 2.2 / 0.0,
(b) 4.1 / 3.0, (c) 3.4 / 4.4, (d) 3.6 / 2.0. Each interval adds the line's half thickness, one
native raster pixel (6 px) and the misfit. Curves are told apart by pattern: the solid line is the
largest connected piece of ink; dots are pieces at most 26 px wide; dashes at least 28 px wide and
at most 30 px tall. Every reading was checked with `boxgraph figure check`; the crosses sit on the
intended curve. Positions where a curve cannot be separated from another were dropped from `at`.

- **Fig. 1(a)-(d)** (p. 4): circuit diagrams. No values. Left out.
- **Table 1** (p. 5): circuit schematics, and two normalised elastance curves (EAtrium, EVentricle,
  E/Emax against t/T). Left out: each curve is a thumbnail about 1 inch wide in a low-resolution
  raster, with only 0 and 1 labelled on the y axis; it shows the shape of the elastance input
  functions of ref [5], not a result, and the functions themselves are defined in
  korakianitis2006. A later pass could read them if a comparison with that record needs it.
- **Figs. 2, 3** (p. 6): block diagrams of the CellML model structure. No values. Left out.
- **Fig. 4** (p. 6): a screenshot of the OpenCell program with three small plots (pressure,
  flow-rate, volume over 0-10 s, coloured lines on black). Left out: a screen capture of a few
  hundred pixels per plot, axis labels barely legible (the flow and volume axes are scaled by
  10^3 and 10^2 in SI units), colours unnamed by any legend, and the run's start-up transient
  dominates; the converged beats are the same simulation shown in Fig. 5, which is read instead.
- **Fig. 5(a) Pressure** (p. 7): read.
  - `fig5a_la` -> `P_la_fig5a`: P(la), the solid line, every 0.05 s from 6.95 to 8.10 s (7.45 s
    included; the line is single there).
  - `fig5a_lv` -> `P_lv_fig5a`: P(lv), the dotted line, on its rise (7.02-7.11 s, 8.02-8.08 s) and
    fall (7.33-7.44 s), where it is apart from the other curves. Where it is steep, two to four
    dots share a column and are read at their span's centre (wider interval). Dots lying on a
    dashed track (the dots of P(sat)'s dash-dot-dot pattern) are excluded. Not read during
    ejection (it overlaps P(sas)) or diastole (it overlaps P(la)).
  - `fig5a_sas`, `fig5a_sat`, `fig5a_svn` -> `P_sas_fig5a`, `P_sat_fig5a`, `P_svn_fig5a`: the three
    dashed tracks (top: P(sas) long dashes; middle: P(sat) dash-dot-dot; bottom: P(svn) short
    dashes), read where exactly three tracks are found: 6.95-7.10 s and 7.40-8.00 s (and 7.20 s for
    P(sat) and P(svn)). The peaks near 7.25-7.3 s are not read: P(lv), P(sas) and P(sat) overlap.
  - No model in this record produces these curves (circulation_fig1d is not runnable); they are
    for the cross-record pass against the CellML and korakianitis2006 records.
- **Fig. 5(b) Flow-rate** (p. 7): read.
  - `fig5b_mi` -> `Q_mi_fig5b`: Q(mi), the solid line, every 0.05 s (7.95 s dropped: the narrow A wave
    rises and falls within that column, two runs).
  - `fig5b_ao` -> `Q_ao_fig5b`: Q(ao), the dotted line, over its ejection spike, 7.12-7.28 s
    (7.10 s is the vertical rise; 7.26 s touches Q(sat)).
  - `fig5b_ao_peak`, `fig5b_mi_peak` -> `Q_ao_peak_fig5b`, `Q_mi_peak_fig5b`: the highest dotted
    and solid ink, one point each. They correspond to the text's "about 1000 mL/s" and "about
    800 mL/s"; being "about" values, a comparison would get no verdict, so none is made. The
    readings are near the printed values (see the build).
  - `fig5b_sat` -> `Q_sat_fig5b`: Q(sat), the only dashed track, every 0.05 s (7.05 s dropped).
    Its intervals are wide (the dashes are short and the track is curved, so extending neighbouring
    dashes to a column spreads).
- **Fig. 5(c) Volume** (p. 7): read.
  - `fig5c_la` -> `V_la_fig5c`: V(la), the solid line, every 0.05 s except 7.45 s (it crosses V(lv)).
  - `fig5c_lv` -> `V_lv_fig5c`: V(lv), the dotted line, every 0.05 s from 6.95 to 8.05 s except 7.45 s.
  - `fig5c_lv_min`, `fig5c_lv_max` -> `V_lv_min_fig5c`, `V_lv_max_fig5c`: V(lv) on its lower plateau
    (7.32-7.40 s) and its two upper plateaus (7.00-7.08 s, 8.00-8.08 s), as minimum and maximum
    left ventricular volume. Compared with the text's 55 mL and 130 mL (`cmp_text_vmin_fig5c`,
    `cmp_text_vmax_fig5c`).
- **Fig. 5(d) Pressure-volume loop** (p. 7): read; one solid curve.
  - `fig5d_esv`, `fig5d_edv` -> `V_lv_min_fig5d`, `V_lv_max_fig5d`: the loop's left and right
    vertical edges, read along rows of constant pressure (x of these readings is pressure, y is
    volume). Compared with 55 and 130 mL (`cmp_text_vmin_fig5d`, `cmp_text_vmax_fig5d`).
  - `fig5d_eject`, `fig5d_fill` -> `P_lv_eject_fig5d`, `P_lv_fill_fig5d`: the upper and lower
    branches every 5 mL from 55 to 130 mL.
  - `fig5d_pmax`, `fig5d_pmin` -> `P_lv_max_fig5d`, `P_lv_min_fig5d`: the loop's highest and lowest
    points. Compared with the text's 120 and 0 mmHg (`cmp_text_pmax_fig5d`, `cmp_text_pmin_fig5d`).

**How the text is compared with its own figure.** The figure and the Section 3 text describe the
same simulation, so the comparisons are `consistency`: six small processing models
(`text_*_over_*`) hold the text's printed value at each position where the figure was read, and
the build compares that with the reading. They give, at the time of this pass: 120 mmHg
reproduced by the loop's top; 0 mmHg not reproduced by the loop's bottom; 55 and 130 mL close to
panel (c)'s plateaus and not reproduced by panel (d)'s edges, whose intervals are narrower. Both
panels agree with each other on the volumes.

**Open questions this pass settles or adds.** q_lv_volume_fig and q_lv_pressure_min_fig (read by
eye before) are settled by the calibrated readings: see q_fig5_lv_volume_read and
q_fig5_lv_pressure_min_read. q_fig5_heart_period notes that Fig. 5 shows the heart period
(about 1 s) the text omits, which bears on q_mean_flow_vs_stroke_volume. q_fig5_arterial_which
records that the text does not say which arterial curve its 80-120 mmHg describes.

**Measurements.** The paper plots no measured data: every plotted value is a model output.
