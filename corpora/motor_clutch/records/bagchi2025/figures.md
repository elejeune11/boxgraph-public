# Figures of bagchi2025: what was read and what was left out

Two passes. The first read the model profiles (Figs 8j-l, 9a-c, 10k, 11k) with
`figures/_panel.py`. The second (this file's new entries) read every other panel that
plots values, with `figures/_kit.py` (points, stars, bars, histograms, box-plot medians,
curves), `figures/_stack.py` (two-colour bars on two y axes) and the per-reading
settings in `figures/_specs.py`. Every reading is calibrated from the image: axis lines
and tick marks found in the crop and matched to the printed tick labels (the only
values typed in). Three calibrations are used:

- `_panel.calibrate`: labelled ticks matched in order (clean vector panels);
- `_kit.calibrate` with `own`/`skip`: the same, checking only the ticks matched;
- `_kit.calibrate_fit`: for bitmaps whose ticks are partly hidden by curves or bars,
  the evenly spaced set of visible ticks counted from the labelled corner of the axes
  (or, for histograms, the ticks hanging from the top frame).

"misfit" is the largest distance in pixels between a calibration mark and the fitted
axis. Intervals are the reading's own 95% interval (line or marker half-size, edge,
misfit). Where an x axis carries categories, x is the position from the left
(`plot_category_index`, `stack_segment_index`, `histogram_bin_index`), named in the
reading's `what`. One code file, `figures/fig4c_af.py`, is left over from a reading that
was dropped (see Fig 4c) and is not used by any reading.

## Fig 1 (p. 4), measured

- 1a, 1b: phase-contrast micrographs. Left out: no values.
- 1c, 1d: cell trajectories coloured by speed. Left out: thousands of overlapping tracks; the colour scale has no readable values per track.
- 1e, 1f, 1i, 1j: kymographs (colour maps). Left out: values only as colour.
- 1g, 1h: leading-edge contours, about 18 colour-coded lines per panel that overlap and cross. Left out: the lines cannot be told apart reliably.
- 1k: `fig1k_af`, the blue circles (strain rate, AF, units of 10^-5 1/s). Small open and filled circles on a dashed line: filled, opened to strip the dashes, centroids; two pairs of touching markers near 820-860 min are merged and left out. calibrate_fit, x 6 marks, y 3 marks.
- 1l: `fig1l_rf`, the same for RF. Three merged pairs left out.
- 1m: `fig1m_af` (red), `fig1m_rf` (blue), velocity autocorrelation; traced curves; x 6 marks misfit 0.95 px, y 4 marks misfit 1.3 px.
- 1n: `fig1n_af`, `fig1n_rf`, chi_4 against Delta t; misfit 2.0 px (x), 0.7 px (y). 160 min left out for RF (the curves cross).
- 1o: scatter of AR against area, m = 56117 and 39447 cells. Left out: tens of thousands of overlapping dots, no individual values.
- 1p: `fig1p_af`, `fig1p_rf`, area distributions; misfit 1.4 px.

## Fig 2 (p. 7), measured

- 2a-2l: micrographs, heat maps and kymographs. Left out: values only as colour.
- 2m: `fig2m_median`, the red median lines of the box plots (1 RF, 2 AF). Quartiles and whiskers are not read. y 3 ticks.
- 2n: `fig2n_tx` (top of the blue Tx segment) and `fig2n_txty` (top of the red Ty segment above it), bars 1 AF, 2 RF; y 7 marks misfit 1.9 px. The small error bars at the segment tops (kind not stated) are not read.
- 2o: `fig2o_af`, `fig2o_rf`, |Tx| along the normalized width. The traces are noisy (hairy); each value is the traced centre at that column with the run's half-height as its interval. RF left out at 0.1 and 0.5 (crossings).
- 2p: `fig2p_af`, `fig2p_rf`, stress correlation; misfit 1.2 px.

## Fig 3 (p. 9), measured

- 3a, 3b: stress ellipses on micrographs. Left out: drawings over images.
- 3c-3g: polar histograms of the alignment angle, AF and RF outlines overlaid in each quadrant. Left out: overlapping outlines in polar coordinates, not readable bar by bar with the tools here.
- 3h, 3i: cumulative distributions of phi for five quintiles, dashed lines. Left out: the three middle quintiles (yellow, green, cyan) overlap within the dash width over most of the range, and the x axis is labelled only on the top frame. The red and blue (outer) quintiles could be read in a later pass.
- 3j, 3k: kymographs. Left out.

## Fig 4 (p. 11), measured

- 4a: `fig4a_af`, red circles, sigma_xx at the midline (AF); filled-and-opened markers, three touching pairs merged and left out; y 3 marks misfit 1.3 px.
- 4b: `fig4b_rf`, the same for RF; only one y tick is visible beside the markers, so the y axis rests on that tick and the labelled corner (1400 Pa).
- 4c: cell area, AF. Left out: the lower labelled tick (200) is hidden under the markers, and the corner is not labelled, so only one tick calibrates the y axis.
- 4d: `fig4d_rf`, cell area, RF; the magenta marker trace, followed from four seeds; 440 min left out (trace broken).
- 4e, 4f: `fig4e_af`, `fig4f_rf`: the same plots as Fig 1k, 1l, read again from this page (two readings of one data set).
- 4g, 4h: cell polygons coloured by area. Left out.
- 4i, 4j: `fig4i_af`, `fig4j_rf`, divisions per time bin; bins between the dark bin edges, the value at the top of the run of bar colour standing on the axis (the red arrow above a bar in 4j is not part of the run); x calibrated on the ticks hanging from the top frame.
- 4k, 4l: `fig4k_af`, `fig4l_rf`, divisions per distance bin; same method; the first tick found (-400) carries its label because the corner is not labelled. The lone low bar near -400 um in 4l is read where its colour stands.
- 4m, 4n: `fig4m_af`, `fig4n_rf`, leading-edge traction against time (noisy traces); y 5 marks misfit 1.2 and 0.8 px.

## Fig 5 (p. 13), measured

- 5a-5n: micrographs, maps and kymographs. Left out: values only as colour.

## Fig 6 (p. 14), simulated

- 6a-6c: schematics. Left out.
- 6d-6g: kymographs. Left out.
- 6h: `fig6h_vel`, leading-edge velocity, connected ligand, traced from three seeds (one per contraction); the spikes at 6 and 13-14 are left out. The x axis is printed "Time (sec)" (question q_fig6h_axis_unit); the y axis rests on the two ticks not hidden by the trace (-150, 100) and the corner (-200).
- 6i: `fig6i_vel`, the same for disconnected ligand.
- 6j, 6k: `fig6j_trac`, `fig6k_trac`, leading-edge traction; misfit 0.9 px.

## Fig 7 (p. 15), simulated

- 7a-7c: `fig7a_conn`, `fig7a_disc`, `fig7b_*`, `fig7c_*`: open circles found by correlating each colour with a ring (radius 48-50 px); the legend is blanked. x misfit 0.8 px, y 0.9 px (7a).
- 7d: `fig7d_disc`: the same; the y axis rests on the ticks 1.5 and 2 (the tick at 1 lies on the frame corner).

## Fig 8 (p. 17), simulated

- 8a-8i: kymographs. Left out.
- 8j-8l: first pass (`fig8j_eps_th`, `fig8k_kc`, `fig8l_eta`).
- 8m: `fig8m_conn` (yellow-filled stars), `fig8m_disc` (cyan-filled stars), 1 no fluidization, 2 fluidization, 3 fluidization with variable stiffness; the fill colour's centroid.

## Fig 9 (p. 18), simulated

- 9a-9c: first pass.
- 9d, 9e, 9g, 9h, 9j, 9k, 9m, 9n: kymographs. Left out.
- 9f, 9i: leading-edge velocity and traction against time, connected and disconnected. Left out: two spiky oscillating traces that overlap and cross every cycle; a value at a fixed time depends on where a near-vertical spike falls.
- 9l: `fig9l_vel`, `fig9l_trac` (`_stack.py`): each bar's red and blue tops, calibrated on the green right axis (the left axis carries the same labels at the same heights). The two readings of the bars (stacked or overlaid) are compared with the printed ratios (question q_bars_stacked_or_overlaid). This settles the reading of q_ratio_statements.
- 9o: `fig9o_conn`, `fig9o_disc`, chi_4; the y axis line is broken and the x axis is covered by the curves, so calibrate_fit (x 3 marks misfit 1.6 px).

## Fig 10 (p. 20), simulated

- 10a: schematic. 10b-10j: kymographs. Left out.
- 10k: first pass.
- 10l: `fig10l_shift`, six asterisks (one per alpha, legend order); strokes joined by closing, centroid.
- 10m: `fig10m_eff`, seven asterisks (6 alphas, 7 connected ligand), right-hand y axis (the panel is read mirrored).

## Fig 11 (p. 21), simulated

- 11a: schematic. 11b-11j: kymographs. Left out.
- 11k: first pass.
- 11l: `fig11l_shift`, five asterisks (one per k_s range).

## S1 Fig (p. 43), measured

- S1a: schematic. S1b, S1c: micrographs. Left out.
- S1d, S1e: `figs1d_af`, `figs1e_uf`, fibre-angle histograms; the x ticks are hidden behind the bars, so x is the bin from the left (9 bins); bins split at their light edges, pieces of equal height a stray line splits are joined.
- S1f: `figs1f_ftir`, the FTIR spectrum; the y axis is printed reversed (-1 at the top), calibrated with the corner 2.5 and a step of -0.5; traced from four seeds; the narrow absorption dips (about 1720-1500 and 1200 cm^-1) are not sampled.

## S2 Fig (p. 44), measured (base condition)

- S2a, S2c, S2d: `figs2a_median`, `figs2c_median`, `figs2d_median`, box-plot medians (1 RF, 2 AF), the wide red line in each box (red "+" outliers are left out by shape). The S2a medians give the AF/RF speed ratio compared with the printed 1.56 (question q_ratio_medians_or_means). S2d: the top y label is printed "2.5" (question q_s2d_axis_label).
- S2b: `figs2b_af`, `figs2b_rf`, speed against time (thick curves); the grey standard-error band is not read.
- S2e: `figs2e_af`, `figs2e_rf`, aspect-ratio distributions; AF left out below AR 1 where the curves coincide.
- S2f: `figs2f_af`, `figs2f_rf`, sigma_xx across the width; the dark error band is within the line.

## S3 Fig (p. 45), measured (softer gel, shorter alignment)

- S3a, S3c: `figs3a_median`, `figs3c_median`, box-plot medians (1 RF, 2 AF); the S3a ratio is compared with the printed 1.34 and 1.33.
- S3b, S3d: `figs3b_af`, `figs3b_rf`, `figs3d_af`, `figs3d_rf`, correlation functions; AF left out below 40 um in S3b where the curves coincide.
- S3e-S3g: polar histograms. Left out (as Fig 3c-g).
- S3h, S3i: cumulative distributions of five quintiles. Left out (as Fig 3h, 3i).

## S4 Fig (p. 46), simulated

- S4a, b, d, e, g, h, j, k: kymographs. Left out.
- S4c, S4f: oscillating leading-edge traces. Left out (as Fig 9f, 9i).
- S4i: `figs4i_vel`, `figs4i_trac` (`_stack.py`), two-colour bars; compared with ~1.7, ~1.8 (p. 16) and with "twice"/"two times" (p. 30).
- S4l: `figs4l_conn`, `figs4l_disc`, chi_4 (the caption calls it (k): question q_si_caption_panels); the x axis line is covered by the curves, so its row is taken from the foot of the y axis.

## S5 Fig (p. 47), simulated

- S5: `figs5_conn` (yellow-filled stars), `figs5_disc` (cyan-filled stars), 1 low density (rho_l = 0.7), 2 high density (rho_l = 1).

## What the figures settle

- q_ratio_statements: the comparisons `cmp_fig9l_*` and `cmp_s4i_*` run both readings of
  the two-colour bars; the stacked reading is the one the printed ratios describe if it
  agrees and the overlaid one does not (q_bars_stacked_or_overlaid).
- q_audit_speed_ratios: the S2a and S3a medians give the experimental AF/RF ratios
  directly (`cmp_s2a_*`, `cmp_s3a_*`).
- q_chain_not_runnable: the simulated readings (Figs 6h-k, 7, 8m, 9o, 10l-m, 11l, S4l, S5)
  are ready to be compared with a run of the authors' code (q_sim_figures_not_compared).
