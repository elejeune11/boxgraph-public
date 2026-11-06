# Figures of Pries et al. 1990

## Read, first pass (line plots, Figs. 1 and 3)

- **Fig. 1, upper panel (p. 4)**: HT/HD against diameter (log axis, 4-100 um) for HD = 0.8, 0.6,
  0.45, 0.3 and 0.1, drawn from Eq. 1. Five readings (`fig1u_HD*`), 14 diameters each, compared
  with Eq. 1.
- **Fig. 1, lower panel (p. 4)**: relative apparent viscosity against diameter for the same five
  HD, drawn from Eqs. 2-3. Five readings (`fig1l_HD*`); the HD = 0.8 curve leaves the panel at
  about D = 24 um and is read only up to 20 um. Compared with Eqs. 2-3.
- **Fig. 3 (p. 6)**: the viscosity of Fig. 1 multiplied by the Eq. 7 factor with W = 3.5 um, for
  the same five HD. Five readings (`fig3_HD*`), from D = 9 um (where all five curves are inside
  the panel) to 95 um. Compared with Eq. 7 as printed and with its corrected variant.

All readings are by the record's own code (`figures/_pries.py`): the frame lines and tick marks
are found in the image, the x axis is calibrated on the five long ticks labelled 5, 10, 20, 50 and
100 under the lowest frame line, the y axis on the ticks left of each panel. The five curves never
cross, so a curve is the k-th from the bottom among the runs of ink in a column; only columns
showing exactly the expected number of curves are used (a dash gap or two merged curves changes
the count), and a quadratic trend through ~40 such columns on either side gives the value.
Diameters where the curve labels stand among the curves (about 30-60 um in Fig. 1 upper, 22-34 and
60-75 um in Fig. 1 lower, 37-65 um in Fig. 3) and the crowded small diameters of Fig. 1 lower
(below 10 um) are not read. The 95% interval is the line's half thickness plus the trend misfit
and the calibration misfits (1-5 px at 1200 dpi).

## Read, second pass (point plots, Figs. 2, 5, 6, 7)

Shared code in `figures/_pts.py`: the plot frame is found as the rows and columns that are mostly
ink; tick marks are the thin ink runs sticking out of a frame line, matched in order to the
printed labels, and where a label stands at a frame line (0 and 1, or 0 and 25) the frame line is
that label's position. Markers: open markers' holes are filled, a morphological opening with a disk
wider than any line removes the lines, and blobs much larger than one marker are split by area. An
open marker is centred on the hole it encloses; a filled one must be solid ink over its disk. A
blob that does not resolve into markers (ink where curves meet an axis) is rejected. The 95%
interval is 2 px of centroid precision plus twice the y calibration misfit, plus a quarter marker
diameter for a marker split from an overlap. None of these figures shows error bars.

- **Fig. 2 (p. 5)**, measured FQE against FQB at one bifurcation, 800 dpi. `fig2_alpha` (filled
  circles, daughter alpha, 13 points) and `fig2_beta` (open circles, daughter beta, 14 points),
  every point at the FQB read from the image. Calibration: ticks 0.25, 0.5, 0.75 on the bottom and
  left edges plus the frame lines at 0 and 1; misfit 1.7 px (x), 1.1 px (y). The legend is
  excluded. A dark blob where both fit lines leave the axis near FQB = 0.11 may hide a marker; it
  does not resolve into one and is not read. The solid lines are the logit fits; their parameters
  and the bifurcation's diameters and hematocrit are not printed, so the phase-separation model
  (Eqs. 4-6) cannot be run on these points. Measured data only. See `q_fig2_domain`: the figure
  bears on `q_phase_separation_domain`.
- **Fig. 5, upper panel (p. 7)**, network A hematocrit distribution, 1200 dpi. `fig5A_meas`
  (filled circles, MEASURED) and `fig5A_pred` (open circles, PREDICTED), each read at its 0.05
  class position. Calibration: ticks 0.2-0.8 above the top frame (the labels are under the lower
  panel, which shares the axis) plus the frame lines at 0 and 1, misfit 7.8 px in x (the frame
  lines sit a few px off the tick grid; the class positions are given, so this does not enter a
  value); y ticks 150, 100, 50 plus the bottom frame line at 0, misfit 2.2 px. Not read for
  MEASURED: 0 (on the corner of the axes), 0.25 (merged with the open marker) and 0.85-1.0
  (merged with the open markers and the axis). PREDICTED is read at all 21 classes.
- **Fig. 5, lower panel (p. 7)**, network C, same method. `fig5C_meas` at the 16 classes 0-0.75,
  `fig5C_pred` at the 14 classes 0-0.65 (no open markers beyond 0.65). y ticks 80, 60, 40, 20 plus
  the bottom frame line; misfit 6.8 px (x), 2.2 px (y).
- **Fig. 6 (p. 7)**, AV velocity against generation, 1000 dpi. `fig6_pred` (open circles, 21
  points, generations 4-24) and `fig6_meas` (filled circles, ref. 17, 8 points), each at the
  generation read from the image. Calibration: x ticks 5-20 plus the frame lines at 0 and 25,
  misfit 2.3 px; y ticks 0.5-2 plus the bottom frame line at 0, misfit 2.4 px. The measured points
  near generations 18.6 and 22 overlap open markers and do not resolve; they are not read.
- **Fig. 7 (p. 8)**, pressure in percent of the total head against diameter class, 800 dpi. The x
  axis is folded (60 ... 0 ... 60); the record reads it as a signed diameter, negative on the
  arterial side. Calibration: the seven ticks above the top frame line, misfit 0.9 px; y ticks
  100-0, misfit 0.9 px. The four series overlap at most diameters, so this figure is read by
  template matching (`figures/_fig7.py`): each template is that series' own legend glyph, and a
  peak counts only if its template beats each of the other three there by 0.06 and scores at
  least 0.5. Each kept position was checked on the overlay. Read: `fig7_modified` (filled
  circles, modified viscosity law) at 14 diameter classes; `fig7_invitro` (open circles, in vitro
  law) at 8; `fig7_zl1977` (filled triangles, Zweifach and Lipowsky, ref. 26, measured) at -20,
  -10 and 40 um; `fig7_zw1974` (open triangles, Zweifach, ref. 25, measured) at -30 um only. At
  the other classes the glyphs lie on top of one another (open against filled triangle, triangle
  against circle) and the matching cannot tell them apart; they are not read. The in vitro peak
  found at 60 um is the word VENOUS and was dropped. The ends (45 um arterial = 100%, 60 um
  venous = 0%) are the normalization, shared by all four series.

No model in the record produces Figs. 5-7 (all are outputs of the network simulation, which cannot
be rerun; see `q_network_not_runnable`), so these readings have no runs. Predicted and measured
series were not compared with each other, because the comparison needs both curves at the same x
values and the readable positions differ between series. A later model that sums a curve could
check the Fig. 5 classes against the segment counts (913, 436) and the Table 3 means and SDs.

## Not read

- **Fig. 4 (p. 6)**: predicted against measured hematocrit, one open circle per segment (913 and
  436). The markers pile on top of one another over most of both panels, so single points cannot
  be told apart. Its printed insets (n, r2) are recorded as values and checked against Tables 1
  and 2.
- **Fig. 8 (p. 8)**: schematic drawings with no values.
