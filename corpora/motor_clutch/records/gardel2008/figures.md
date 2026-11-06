# Figure readings: gardel2008

All readings are made by the record's own code (`figures/*.py`, helpers in `figures/_*.py`), which every
build runs on the crop it renders at the reading's dpi. Axes are calibrated from the image: the plot
frame (the longest dark lines), the tick marks (long and short ticks found on the edges; where ticks
appear on two opposite edges, the shorter length is used, so a marker touching a tick does not turn it
into a long one) and the printed labels matched to them; a frame edge is used as a mark only where it
lies on the tick grid. Misfits below are the largest distance of a mark from the fitted axis line.
Every reading was checked with `boxgraph figure check` and its overlay looked at (`figwork/<id>.png`).
Each reading has a datum `<reading id>_data` in data.yaml (origin `measured`).
Conditions are numbered 1 CONTROL, 2 BLEB, 3 CA-RAC, 4 CA-RHO; cell regions 1 BG, 2 LP, 3 FA, 4 CB.

The earlier pass read no figure (q_figures_not_read); this pass reads every data panel listed there
except Fig. S2 H (below). See q_fig4d_read.

## Fig. 1 (PDF p. 2)

- A, B, C, E, H: micrographs, vector maps and heat maps; no values to read. Left out.
- D, box plots of traction stress per region (BG, LP, FA, CB): read: `fig1d_median`, `fig1d_q1`,
  `fig1d_q3`, `fig1d_whisker_lo`, `fig1d_whisker_hi`, one reading per statistic, each a full-width
  horizontal stroke (median red, box bounds blue, whisker caps black). y from the five left ticks
  (200 at the topmost, step 50), misfit about 1 px; categories at the bottom ticks. The notches (95% CI
  of the median) and the outlier + marks are not read.
- F, box plots of F-actin speed per region (LP, FA, CB): read the same way, `fig1f_*` (y: 30 at the
  topmost tick, step 10, misfit 0.4 px).
- G left, histogram of F-actin speed over the entire cell front: read bar by bar, `fig1g_front`
  (30 bars). x from the long ticks 5-25 and both frame edges (0, 30), y from the ticks and edges 0-6000;
  bar edges are the vertical outline strokes, fitted to a regular grid (a black tick drawn over an
  outline can hide it): the bins come out 1 nm/s wide from 0. Bar top = centre of the top stroke.
- G right, histogram at the >95% stresses: read bar by bar, `fig1g_peak` (18 bars, 0-18 nm/s). Bins
  where only a sliver of red lies on the axis (about 18-21 nm/s) are not read. The printed "~8 nm/s"
  mean of this distribution (v_peak_gaussian_mean) can be checked against these bars once the record
  has a processing model for the mean of a histogram; none is written here.

## Fig. 2 (PDF p. 3)

- A, C: heat map and immunofluorescence image. Left out.
- B, + BLEB: read: `fig2b_stress` (green dots, mean traction stress) and `fig2b_speed` (blue line at its
  vertices, F-actin speed), against distance from the cell edge. x from the black ticks every 2 um,
  anchored on the right frame edge (0; misfit 2 px); y from the green ticks of the left axis (10, 20, and
  the frame edges 0 and 30; misfit 3.6 px). The blue right-axis ticks (10, 20) lie on the same rows; the
  code checks that the two axes share their scale. 28 of the 30 dots are read: the one cut by the right
  frame edge and one fused into a cluster are not. The blue line is read at the dots' distances (its
  vertices are there); on steep segments the interval spans the line's run in that column.

## Fig. 3 (PDF p. 4)

- A, B: scatter clouds of thousands of overlapping points (grid points, coloured by group). Left out:
  the points cannot be told apart.
- C: micrograph with group markers. Left out.
- D (top): montage of images. Left out. D rows 2-5, time courses of one FA: read: `fig3d_area`,
  `fig3d_paxillin`, `fig3d_stress`, `fig3d_speed` (26-29 dots each). x from the long ticks (0, 2, ..., 14;
  0 at the left frame edge, misfit 4 px on this coarse raster); y from the long ticks, anchored on the
  bottom edge (0). The dashed 75% line, the "ts" text and arrow are excluded by size and shape. The
  stress row has no dot at 10.5 min (none is drawn there).
- E: v(ts) against ts, `fig3e_points` (27 marker positions; one stack at about 2 min is split into its two
  ends and may hide a third dot). x misfit 1.7 px, y 1.6 px.
- F: v(ts) against sigma(ts), `fig3f_points` (32 dots). The x axis is calibrated on the ticks labelled
  40-120: the "0" at the left frame edge does not lie on the tick grid (q_fig3f_axis_zero).
  The mean and SD of the read points agree with the caption's printed means in both panels, which
  supports the calibration; the counts (27 and 32) differ from each other and from the 26 FAs of the
  caption (q_fig3ef_point_count).

## Fig. 4 (PDF p. 5)

- A: scatter cloud. Left out. B: micrograph. Left out.
- C left, mean traction stress against cell edge distance, four characteristic cells: read:
  `fig4c_dist_control` (18 markers), `fig4c_dist_bleb` (22), `fig4c_dist_carac` (12), `fig4c_dist_carho`
  (24). Markers by colour after an opening that removes the lines; a marker fused with another colour's
  is not read (not guessed); legend markers are recognised by the text to their right and dropped.
  x misfit 2 px, y 0.9 px.
- C right, against F-actin speed: `fig4c_speed_control` (11), `fig4c_speed_bleb` (11),
  `fig4c_speed_carac` (10), `fig4c_speed_carho` (10). The crowded markers below about 3 nm/s, where the
  four lines and their error bars overlap, are not read. The small horizontal and vertical error bars of
  this panel are not read either: they are unidentified in the legend and lie on top of each other and
  of the markers, so their ends cannot be told apart reliably.
- D left: `fig4d_distance`, D right: `fig4d_speed`: mean (square) and SD (error bars, identified in the
  legend) per condition. x from the long and short ticks; in the right panel the left frame edge is 0.5
  nm/s off the tick grid (not used) and in the left panel the right edge is 0.5 um past the "0" tick; the
  ticks carry the labels (misfit 3.6 px on a raster drawn at about half the render resolution). Bar ends
  are the centres of the end caps. The speed reading is compared with the threshold claim run per
  condition: `cmp_threshold_vs_fig4d` (validation).

## Fig. 5 (PDF p. 6)

- A-D: scatter clouds with fitted lines and arrows. Left out: thousands of overlapping points; the
  arrows mark vs, vw, sigma_s, sigma_w, which E-G plot as numbers.
- E: `fig5e_ms` (blue) and `fig5e_mw` (red); F: `fig5f_sigma_s`, `fig5f_sigma_w`; G: `fig5g_vs`,
  `fig5g_vw`. Means with error bars per condition (unidentified in the legend: q_fig5_error_bars,
  `error_bars: unstated`). y from the long ticks (E: 30 at the topmost, F: 140, G: 25 with 30 on the top
  edge), misfits 1.6-1.9 px; condition columns from the long ticks of the top and bottom edges. Where a
  red marker covers a blue one (or caps cover a marker), the visible part is shorter than the marker,
  and the centre's interval is widened by half the hidden part. Hidden bar ends are taken as the mirror
  of the visible end, and the reading says so (BLEB in E blue, F red, G red). These readings let
  q_not_significant_untested be checked with calibrated values instead of the eye.
- H: drawing of the model. Left out (no values).

## Fig. S1 (PDF p. 8)

- Images only. Left out.

## Fig. S2 (PDF p. 9)

- A, E, G: images and vector maps. Left out. B, C, F: scatter clouds (F with trajectories over a grey
  cloud). Left out: points cannot be told apart.
- D, normalized stress against normalized speed across single FAs: read: `figS2d_points` (37 asterisk
  centres; one tightly overlapping pair near (0.84, 0.43) gives one). The ticks are read as steps of
  0.2: the "1" labels sit at the frame edges, 5.5 tick steps from 0, and points normalized to exactly
  1 fall on the fifth tick (q_figS2d_axis_ends). Misfits 1.4 and 1.8 px.
- H, time courses of three FAs (four strips): left out. In each strip the tick spacing is uneven by
  about 7% (e.g. the edge-distance strip: 10 to 5 and 5 to 0 differ by 66 px at 1800 dpi), so no linear
  axis fits the ticks within a marker's size, and the oval markers of the three colours touch and fuse
  along each line. A reading attempt was made and dropped.

## Fig. S3 (PDF p. 10)

- A, C: scatter clouds; B, D: images with markers. Left out.
- E: `figS3e_rat`, r_AT of the high-speed data against v0 (21 blue squares; grey ticks, misfits 1.9 and
  0.9 px). Squares chained at small v0 are separated by a square erosion; where two centres are too
  close for two cores, the two ends of the core are taken and the interval widened.
- F: `figS3f_rat`, r_AT of the low-speed data against v0 (28 red triangles; x from -5 to 45, misfit
  3.9 px). In the dense chain between 6 and 9 nm/s not every triangle is separated; the reading has the
  separable ones and says where markers may hide.
