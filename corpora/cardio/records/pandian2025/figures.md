# Figures of pandian2025

Figure pass of 2026-11-12. Every reading is made by the record's own code (`figures/*.py`) on the page region
rendered at the reading's dpi, and checked on its overlay (`figwork/<reading id>.png`). All figures are raster
images embedded in the PDF. Axes are calibrated from the image: the axis lines are the darkest column/row, the
major ticks are dark runs outside the axes, matched in order to the printed labels, and a straight line is fitted
(log axes: to the printed exponents). The largest tick misfit widens every interval. Shared code: `_axes.py`
(calibration), `_cols.py` (column plots), and one `_figNN.py` per panel family.

The captions do not say what the central lines, whiskers, bars and error bars are. The whiskers end at the
outermost dots, as a range would. The Fig. 4a bars equal the mean of their dots (`cmp_pd_mean_vs_bars`). Readings
with whiskers or error bars declare `error_bars: unstated`, so the build takes the whisker range as the printed
interval. Verdicts against those data are therefore loose (`q_fig_cfd_vs_beads`).

An earlier pass read only the Fig. S5 colour-bar labels, by eye at 110 dpi. Those labels were re-read at 1200 dpi
here, and `s5c_v_max` was corrected from 22.4 to 72.4 (`q_s5_labels_1200dpi`).

## Fig. 2 (p. 5)

- **2a, read**: `fig2a_inhouse`, `fig2a_muves`, `fig2a_reaver` (900 dpi). These are every marker of the three
  series, 7 vessels each, x = manual diameter. Calibration: 5 + 5 ticks, misfit 0.45 px (1 um is about 42 px).
  - Pink squares are found by matching a square minus its surrounding ring. This matters because three squares
    sit on their own fit line, which pulls a plain distance maximum along the line.
  - Teal diamonds are distance-transform cores. The two overlapping diamonds near 21 um are split at the ends of
    their joint core.
  - Blue open rings are found by annulus correlation, after the dashes of the fit line are removed.
  - The three series place the vessels at the same manual diameters.
  - Run through `r2_linear_fit`, the points reproduce all three printed R2 values (`cmp_r2_*`;
    `q_fig2a_r2_line`).
- **2b, read**: `fig2b_n1`, `fig2b_n2`, `fig2b_n3` (900 dpi). These are the three grey polylines, read at their
  vertices, told apart by grey level (core about 169, 122 and 5). Calibration: 5 + 5 ticks, misfit 1.0 px.
  Interval widening:
  - on steep segments and line ends, by half the run's excess over the line thickness;
  - where Network-1 and Network-2 overlap at threshold 0.3, by half a thickness;
  - at 0.4, where Network-3 merges with the x axis, by half a thickness.
  - No model in the record uses these readings.
- **2c-g, left out**: micrographs, renderings and a colour map of surface deviations. They have no axis to read.
- **2h, left out**: the node-count histograms of three networks are drawn as overlapping translucent curves with
  shaded bands. They peak at the same place, so the networks cannot be told apart. The text's "97% within 25 um"
  is a percentage of points, which these curves cannot give.

## Fig. 3 (p. 6; caption p. 7)

- **3a, 3b, 3d, 3g, left out**: micrographs and streamline or colour renderings. The colour bars carry only end
  labels.
- **3c, read**: `fig3c_vmax` (black circles, left axis) and `fig3c_time` (grey circles, right axis), at 1500
  dpi. These are three meshes. Calibration:
  - left and right axes: 5 ticks each, misfit 2.0 px;
  - x axis: 16 ticks at 1e6 steps, misfit 3.2 px.
  - The readings can be set against the text's "within a 5% error" (p. 5). That sentence is a bound, not a value,
    so it is not entered as a comparison.
- **3e, read**: `fig3e_radius` (1500 dpi). This is the black central line of each network, plus the grey whisker
  caps. Calibration: 6 ticks, misfit 2.05 px. It bears on `q_diameter_radius` (`q_fig_radius_text`).
- **3f, read**: `fig3f_expt` and `fig3f_cfd` (1200 dpi, log axis). These are the central lines and whiskers of
  the six columns, indexed by network. Calibration: 5 ticks, misfit 1.6 px. Comparison:
  `cmp_fig3f_cfd_vs_beads` (validation; `q_fig_cfd_vs_beads`).
- **3h, read**: `fig3h_wss` (1500 dpi, log axis). These are the dashed central lines. There are no whiskers, and
  the extreme single dots were not read. Calibration: 5 ticks, misfit 1.75 px. See `q_fig_wss_medians`.
- **3i, read**: `fig3i_interstitial` (1200 dpi, log axis). These are the central lines. Calibration: 4 ticks,
  misfit 0.6 px.
- **3j, left out**: about a thousand overlapping translucent points with no axis-aligned structure, too dense to
  read point by point. Its R2 (0.864) needs the regression coefficients (`q_wss_regression`).

## Fig. 4 (p. 8)

- **4a, read**: `fig4a_bars` (bar tops and upper error-bar caps) and `fig4a_points` (every dot: 13 control and
  11 IL-1beta), at 1500 dpi.
  - Calibration: 5 ticks, misfit 1.75 px. The axis reads in 10^-6 cm/s, but the readings are recorded in nm/s
    (x 10), because the unit parser drops a numeric factor in a unit such as `1e-6*cm/s`.
  - Bar tops: the median over the columns where the bar's own edge is visible.
  - Error bars: the lower half of each is hidden in the bar and taken as the mirror of the upper half.
  - Comparisons: `cmp_pd_mean_vs_bars` (the bars are the means of the dots) and `cmp_pd_printed_vs_bars` (the
    Sect. 4.11 values at the bars). This settles the unit question `q_pd_unit` towards m/s (`q_fig4a_pd_values`).
- **4b, read**: `fig4b_median` (thick dashed line), `fig4b_q3` and `fig4b_q1` (the dotted lines above and
  below it), and `fig4b_networks` (the three large black dots per group), at 1500 dpi. Calibration: 6 ticks,
  misfit 2.6 px. Two things are kept out of the search:
  - the 'ns' bar, by searching only below 90 um;
  - the violin outline, by counting only thin dark pixels in a narrow window.
- **4c, read**: `fig4c_median` (dashed central line) and `fig4c_networks` (three dots per group), at 1500 dpi on
  a log axis. Calibration: 5 ticks, misfit 1.5 px. The dots are excluded from the line search by their thickness.
- **4d, left out**: micrographs and velocity-vector renderings.
- **4e, read**: `fig4e_control` (t = 1-7 s) and `fig4e_il1b` (t = 2-7 s; at t = 1 s the grey point is hidden
  behind the black one), at 900 dpi. Calibration: 5 + 8 ticks, misfit 0.55 px. The legend's markers are excluded.
  See `q_fig4e_pressures`.
- **4f, read**: `fig4f_expt` and `fig4f_cfd` (1200 dpi, log axis), read as in 3f. Calibration: 4 ticks, misfit
  0.8 px. Comparison: `cmp_fig4f_cfd_vs_beads`.
- **4g, read**: `fig4g_wss` (1200 dpi, log axis): the dashed central lines. Calibration: 6 ticks, misfit 1.8 px.

## Supplement (pp. 14-17)

- **S1-S4, left out**: these are renderings and drawings with no axes.
  - S1 is the discretized geometry.
  - S2 shows streamline renderings of the six networks; their colour bars carry only end labels.
  - S3 shows wall shear stress renderings in Pa, although its caption repeats S2's "Streamlines (mm/s)".
  - S4 is a device drawing and micrographs.
- **S5a, left out**: a drawing. Its dimension labels (R = 25 and 125 um, t = 10 um) are noted in `data.yaml`.
- **S5b-c, colour maps left out; colour-bar end labels recorded as printed numbers**: 28, 9.82 Pa and 29.1,
  9.39e-6 mm/s for the control; 28, 9.87 Pa and 72.4, 6.75e-5 mm/s for IL-1beta. These were checked at 1200 dpi.
  The colour maps themselves give no value that can be located.

## Not compared

The network CFD results (3c, 3f CFD, 3h, 3i, 4f CFD, 4g) and the grid-model curve (4e) are produced by COMSOL
models that the record cannot run (`q_cfd_not_runnable`). They are recorded as data for later papers' models and
compared only with each other and with the beads.
