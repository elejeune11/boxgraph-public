# Figures of kassab1993

Figs. 6-11 are read by the record's own code (`figures/_kassab.py`, with each figure's axis labels
and legend boxes in `figures/_figN.py`), one reading per tree: `figN_rca` (open squares), `figN_lad`
(open triangles), `figN_lcx` (open circles). All are 1200 dpi renders of black-and-white scans.

How they are read, in short:
- **Calibration.** The crop is straightened by the tilt of its longest line. Ticks are runs of ink
  sticking out of an axis on its outer side only, so markers sitting on the axis are not taken as
  ticks.
  - The decades of the log axes are unevenly spaced in these scans (by up to 15%), so log axes are
    calibrated piecewise through the decade ticks and the unlabelled 2..9 ticks.
  - Ticks hidden under markers are skipped.
  - When the lowest label lies on the x axis, half the axis line's thickness is added to the
    misfit.
- **Points.** The marker glyphs are cut out of the legend and matched in a window at each order.
  Each glyph pixel is weighted by how far it lies from the other glyphs' outlines, so a square must
  show its corners and a circle its arcs. The value is the glyph's centre.
- **Hidden or ambiguous markers.** The three trees' markers often overlap (identical values, error
  bars, the fitted lines through them). A marker is read only when its outline is found, its place
  is unambiguous, and it is not explained by a better-matching marker of another shape.
- **`at` and the overlays.** Each reading's `at` lists the orders where its marker was found. Every
  read point was checked on zoomed patches of the overlay (`figwork/tiles_<id>.png`); the Fig. 8
  LAD orders 3, 4 and 7 were dropped there, because a bar cap stacked on the LCX circle had been
  taken for a triangle.
- **Error bars** are read only where the stem is unambiguous: not when the marker sits on the y axis
  or another series' marker lies along the bar. As a result most bars in Figs. 7-9 and 11 are not
  reported, and only the LCX bars of Fig. 10 are.

Each reading is compared with what produces it:
- **Figs. 6-9** against the table values they plot (`order_*` lookup models, purpose consistency).
- **Figs. 10-11** against Eqs. 6a and 7a (`order_csa_*`, `order_volume_*`, purpose reproduction).
  The inputs are either the element mean diameters (as `tree_volume_*`) or the segment mean
  diameters (`*_segD`).

- **Figs. 1-5**: left out.
  - They are a perfusion diagram, micrographs, cast photographs, order-numbering drawings and trunk
    sketches.
  - Fig. 5 prints (diameter, length) pairs of each trunk segment as text, not plotted values. Its
    OCR is garbled and the pairs feed no model of the paper.
- **Fig. 6** (p. 10), mean element diameter, log axis 1-10000 um: read.
  - Calibration: 32 ticks, misfit 16 px (8 px of it the axis line), about 423 px per decade.
  - `fig6_rca`: orders 1, 2, 4, 5, 8, 10, 11.
  - `fig6_lad`: orders 9-11. The other triangles are hidden inside the squares and circles; Table 2
    has orders 1-3 equal to Table 3.
  - `fig6_lcx`: orders 1-10.
  - All points agree with Tables 1-3 (`cmp_fig6_*` reproduced).
  - The Eq. 2 lines are not read: the three lines overlap, and Table 4 prints their constants.
- **Fig. 7** (p. 10), mean element length with error bars, log axis 100-100000 um: read.
  - Calibration: 27 ticks, misfit 14 px, about 564 px per decade.
  - `fig7_rca`: orders 2, 4, 9, 11.
  - `fig7_lad`: orders 10, 11.
  - `fig7_lcx`: orders 1-10.
  - The bars are not reported: they overlap between trees in every column read. The caption does not
    say what they are; Tables 1-3 give SD.
  - All points agree with Tables 1-3 except the RCA order 11 square. It is isolated and clear, and
    is drawn below the 84.1 mm of Table 1 (`cmp_fig7_rca` close; `q_fig7_rca_order11`).
  - The Eq. 4 lines are not read: they overlap.
- **Fig. 8** (p. 11), S/E with error bars, linear axis 0-30: read.
  - Calibration: 7 labelled ticks, misfit 13 px (7.5 px of it the axis line), 57 px per unit.
  - `fig8_rca`: orders 2, 11.
  - `fig8_lad`: orders 10, 11.
  - `fig8_lcx`: orders 1-9.
  - Orders 1-9 of the three trees lie on top of one another. The bars, unstated in the caption (Table
    5 gives SD), are read only where no other marker shares the column: at RCA and LAD order 11, at
    most the marker.
  - All points agree with Table 5 (`cmp_fig8_*` reproduced).
  - The 5th-order polynomial curves are not read: their coefficients are not printed and the three
    curves cross and overlap below order 9.
- **Fig. 9** (p. 12), total number of elements with error bars, log axis 10^0-10^6: read.
  - Calibration: 29 ticks, misfit 17 px, about 292 px per decade. The 10^5 and 10^4 ticks are hidden
    by the order-1 markers on the axis, and the order 10 and 11 x ticks by markers on the x axis.
  - `fig9_rca`: orders 1, 2, 3, 9, 10.
  - `fig9_lad`: orders 1-5, 7, 9-11.
  - `fig9_lcx`: orders 1, 2, 4-9.
  - The bars are not stated in the caption (Table 9 gives SE). They are reported at LAD order 11 (at most
    the marker) and LCX orders 5 and 9 (lower end hidden in the circle, so taken as the mirror of the
    upper).
  - All points agree with Table 9 except the RCA order 3 square, drawn around the LAD triangle
    (close; `q_fig9_rca_order3`).
  - The Eq. 5 lines are not read (RCA and LAD lines overlap). Their fall with order supports
    `q_number_slope_sign` (`q_fig9_line_slope`).
- **Fig. 10** (p. 12), total CSA of each order with SE bars, linear axis 0-0.5 cm2, order axis
  reversed: read.
  - Calibration: 5 labelled ticks (the 0.1 tick is hidden by the order-11 markers), misfit 12 px,
    36 px per 0.01 cm2.
  - `fig10_rca`: orders 1, 3, 5-8, 10.
  - `fig10_lad`: orders 1-11.
  - `fig10_lcx`: orders 1-10. SE bars are read at orders 4 and 5. At orders 6-10 no bar sticks out of
    the circle, so the bar is at most the marker; LAD order 10 is the same.
  - Eq. 6a with the element mean diameters falls below several RCA and LAD points (`cmp_fig10_rca`,
    `cmp_fig10_lad` not reproduced).
  - With the segment mean diameters of Tables 1-3 and the element numbers of Table 9, every point is
    reproduced except one close RCA point (`cmp_fig10_*_segD`). This settles which diameter the
    paper used (`q_fig10_segment_diameters`, bearing on `q_volume_rca`).
  - The fitted curves are not read: they are smoothing polynomials whose coefficients are not printed.
- **Fig. 11** (p. 13), blood volume of each order with SE bars, log axis .0001-1 ml, order axis
  reversed: read.
  - Calibration: 29 ticks, misfit 16 px, about 457 px per decade.
  - `fig11_rca`: orders 2, 3, 10, 11.
  - `fig11_lad`: orders 1-5, 7, 11.
  - `fig11_lcx`: orders 1-10. An SE bar is read at order 9 (upper end hidden in the circle, so taken
    as the mirror of the lower).
  - Eq. 7a with segment diameters, element lengths and element numbers reproduces the RCA and LAD
    points and all but one (close) LCX point (`cmp_fig11_*_segD`). With element diameters it is
    only close for RCA and LAD, and not reproduced for LCX.
  - Summed over orders, the segment-diameter reading reproduces all three printed cumulative volumes
    (`cmp_volume_*_segD`).
  - The connecting lines are not read: they only join the points.
