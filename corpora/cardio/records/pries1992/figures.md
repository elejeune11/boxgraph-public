# Figures of pries1992

All readings are `mode: code` (`figures.yaml`, code in `figures/`). Shared helpers: `_p92.py`
(straightening by the scan's tilt, frame and tick finding, line reading by columns),
`_fig5.py` (Figs. 2 and 5), `_fig6.py`, `_fig3.py`. Every reading was checked with
`boxgraph figure check`; the magenta marks sit on the intended line or marker. Calibration
misfits below are in pixels at the reading's dpi.

The earlier pass read no figures (the rendering commands were not available to it); its
eye-read values (`eta045_large_tubes` ~3.2, `eta045_minimum` ~1.25, `D_minimum` ~7) are kept
unchanged.

- **Fig. 1 (p. 3)**: drawing of the capillary viscometer. Left out: no values.
- **Fig. 2 (p. 4), main panel, fitting line**: read, `fig2_eq2` (900 dpi). The broken Eq. 2
  line, only where it stands clear of the data letters: its steep descent below the letter Z
  (D = 3.3, 3.6, 4 um) and beyond the last letters (D = 1,200-2,300 um, the lowest run between
  3.05 and 3.35, since the thin line joining the letters C runs just above). Calibration: 30
  log x ticks below the bottom frame (1 to 3,000) interpolated between bottom and top rows of
  ticks (offset up to 9 px), 8 y ticks every 0.5 (4.5 at the frame to 1) interpolated between
  left and right sides (offset up to 9 px). Compared with Eq. 2 (`cmp_fig2_eq2`).
- **Fig. 2, main panel, data**: left out. The 163 values are drawn as letters (one per study)
  joined by thin lines, crowded along the fitting line between 5 and 300 um; a letter has no
  well-defined reference point and most overlap their neighbours. The same 163 values are
  plotted as filled circles in Fig. 5 (read there, `fig5_points_HD045`) and, as residuals from
  Eq. 2, in the inset (read, below).
- **Fig. 2, inset**: read, `fig2_residuals` (1200 dpi): the filled circles, residual of eta_rel
  from Eq. 2 against diameter; about 152 of the 163 markers found (merged clusters split into
  disks; a split marker gets an interval of half a marker radius). Calibration: 30 log x ticks
  (1 to 3,000), 7 y ticks each side (0.6 to -0.6). New quantity `viscosity_residual_eq2`.
  No model in the record predicts residuals by itself, so it is recorded without a comparison.
- **Fig. 3 (p. 5), lines**: read, `fig3_44um_line`, `fig3_56um_line`, `fig3_6um_line`,
  `fig3_9um_line`, `fig3_12um_line`, `fig3_20um_line`, `fig3_40um_line` (1200 dpi). Per panel:
  11 x ticks (0 to 1) below the bottom frame, y ticks both sides (top tick at the top frame),
  misfits x 3-6 px, y 3-9 px. Markers are masked first; a position is read only if at least 12
  of 41 columns show the line between markers and those columns follow one trend (sd at most
  5 px), so the lines are read at a few positions each (1 for 5.6 um, 2 for 6 um, 4-10
  elsewhere). Compared with Eq. 3 and the Table 2 B and C of the panel (new model
  `eq3_eta_hct`; 20 um uses the 1.85 cP row, n = 59 as in the panel).
- **Fig. 3, 3.3 um line**: left out: it runs through dense filled circles over its whole length
  and no position passed the test above (`figures/fig3_33um_line.py` is an unused stub).
- **Fig. 3, points**: read, `fig3_33um_points`, `fig3_44um_points` (open circles, found as the
  round holes of the ink; gaps enclosed by filled markers are rejected), `fig3_56um_points`,
  `fig3_6um_points`, `fig3_9um_points`, `fig3_12um_points`, `fig3_20um_points`,
  `fig3_40um_points`. Markers found against the n printed in each panel, about: 3.3 um 55/72,
  4.4 um 59/96 (open circles hidden under filled ones have no hole), 5.6 um 27/44,
  6 um 87/170, 9 um 37/45, 12 um 44/60, 20 um 47/59, 40 um 48/64; the rest are fully hidden in
  merged clusters. Compared (fit_quality) with Eq. 3 and the B, C fitted to each set.
- **Fig. 4 (p. 6)**: read, `fig4_eq4` (900 dpi): the broken Eq. 4 line at 15 diameters (7-8.5 um
  on the steep descent, right of the thin data line; 12, 18, 40 um near the minimum; 200-2,500
  um on the plateau). Calibration: 30 log x ticks below the bottom frame (1 to 3,000, misfit
  6.7 px), 7 y ticks (1.5 to -1.5, misfit 5.0 px). Compared with Eq. 4 (`cmp_fig4_eq4`). The
  letters (C per data set) are the values printed in Table 2, already in the record; the thin
  line joining them is not read.
- **Fig. 5 (p. 6), lines**: read, `fig5_HD060`, `fig5_HD045`, `fig5_HD020` (900 dpi): the
  broken H_D 0.60 and 0.20 lines (Eq. 7) and the solid 0.45 line (Eq. 2). Calibration as
  Fig. 2 (x ticks top-bottom offset up to 18 px, y ticks left-right up to 13 px, both
  interpolated); markers masked; each position reads the top or bottom run within a value band
  chosen to keep out letters, thin lines, legend and labels (listed in the code). Compared with
  Eq. 7 / Eq. 2.
- **Fig. 5, points**: read, `fig5_points_HD045`: the filled circles (compiled data at 0.45;
  the caption's "Fig. 1" means Fig. 2, see `q_fig5_caption_fig1`); about 140 of 163 found.
  Compared (fit_quality) with Eq. 2.
- **Fig. 5, letters (data at H_D 0.2 and 0.6)**: left out: letters joined by lines, crossing the
  curves; no reference point for a letter can be found reliably.
- **Fig. 6 (p. 7)**: read, `fig6_HctT06`, `fig6_HctT045`, `fig6_HctT02` (heavy lines, fixed tube
  hematocrit) and `fig6_HctD06`, `fig6_HctD045`, `fig6_HctD02` (thin lines, fixed discharge
  hematocrit), 1200 dpi. A line is chosen by thickness (heavy at least 10 px) and rank among
  columns showing exactly three of its kind; D = 12-200 um for all six, 300-700 um for the
  heavy lines (the thin ones merge into them there). Calibration: 28 log x ticks (2 to 2,000,
  misfit 2.7 px), 9 y ticks (5 to 1, misfit 7.0 px; the half ticks sit a few px off the midpoints
  on both sides). Heavy lines compared with Eq. 10 then Eq. 7 (new model `eq7_tube_hct`), thin
  lines with Eq. 7.

## What the figures settle

- `q_eq10_root_small_D`: by eye on the rendered crop, every curve of Fig. 6 starts at about
  D = 3.1-3.3 um, not at the axis origin 2 um, i.e. just above the 3.06 um where X of Eq. 9
  reaches 1. So the figure does not show values from the problematic root below 3.06 um; the
  curves simply begin there. Recorded as `q_fig6_start`.
- The 6 um line of Fig. 3 rises above Eq. 3 with its Table 2 B and C at high H_D
  (`q_fig3_6um_line`).
- The steep parts (D < 4.5 um) of the Eq. 2 line in Figs. 2 and 5 and of the Eq. 7 lines in
  Fig. 5 lie below the printed equations, while their large-diameter ends agree: see
  `q_fig_eq2_steep`.
