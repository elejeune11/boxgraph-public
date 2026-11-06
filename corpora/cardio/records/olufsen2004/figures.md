# Figures of olufsen2004

- Fig. 1 (p. 4): drawing of the vessel geometry. No values.
- Fig. 2 (p. 8): tau versus R with the six time-scales as horizontal lines; model output only, no
  measured data. Read at 900 dpi, crop [2400, 1500, 5280, 3810] (plot box about 2500 x 1980 px),
  with reading code (`figures/_fig2.py`). Calibration from the image: the black plot frame gives
  the axis limits printed at its corners (R 0 and 1.5 cm, tau 0 and 0.25), and the interior tick
  marks on the top and right edges are matched to the labels 0.5, 1 and 0.05-0.2; the misfit of
  both straight-line fits is under half a pixel.
  - `fig2_tau` (datum `tau_fig2`): the blue curve at R = 0.2-0.8 and 1.2-1.4 cm. R = 0.9-1.1 cm
    is left out because the curve runs under the solid green lambda_p line there, and R < 0.18 cm
    because the curve is above the plot box. The curve is drawn as a polyline (vertices about
    0.025-0.03 cm apart), so each interval carries the offset of the centre from the chord over
    50 columns either side, besides line placement and slope; this dominates at small R (about
    +-0.01 at R = 0.2). Compared (`cmp_fig2_tau`) with tau = T nu/(2 pi R^2) at the printed
    nu = 0.046 cm^2/s and HR = 1 beat/s (model `tau_vs_radius`).
  - `fig2_lq1`, `fig2_lq2`, `fig2_lp1`, `fig2_lp`, `fig2_lp2` (data `lambda_*_fig2`): the five
    horizontal lines (lambda_q = lambda_q1 is one line), told apart by colour and order from the
    top, with the line style (solid or broken) checked against the legend; each read at R = 0.1
    and 0.6 cm, away from the blue curve and the legend, as the median centre over 160 columns.
    Compared with the time-scales computed from beta_1, beta_2 (model `timescale_lines`, the
    arithmetic of Eqs. 18-20).
  - Open questions: this reading settles q_fig2_not_read (the figure is now digitised, and its
    curve and lines can be checked against the printed formula and values). For q_threshold_05
    the figure shows the blue curve meeting the dashed lambda_p1 line near R = 0.44 cm, as that
    question says; the figure does not mark a threshold at 0.5 cm.
- Fig. 3 (p. 12) and Fig. 5 (p. 17): circuit drawings. No values.
- Fig. 4 (p. 14): flow q against time t after a pressure step, solid (rigid vessel) and dashed
  (windkessel; the caption says dotted, see q_fig4_caption_dotted). An earlier pass called this a
  sketch with no numbered axes; it has numbered axes (t -2 to 2, q -3 to 10) and is read now.
  Read at 1200 dpi, crop [3790, 2000, 6410, 4080] (plot box about 2230 x 1760 px), with reading
  code (`figures/_fig4.py`). Calibration from the image: the frame's left and right edges are
  t = -2 and 2 and the top-edge ticks are t = -1, 0, 1; the top edge is q = 10 and the left-edge
  ticks are q = 8 to -2 (the unlabelled bottom edge is not used); misfit under half a pixel on both
  axes. Both curves are drawn as polylines with vertices every 0.1 in t, so each interval carries
  the offset from the chord over 60 columns either side, besides placement and slope; the
  intervals are wide on the steep part (about +-0.9 at t = 0.1).
  - `fig4_rigid_before` (datum `q_rigid_before_fig4`): the flat solid line at t = -1.5, -0.75,
    -0.25 (q = 9.428). It is pi p0/8 and is the basis of the added p0 = 24 (`p0_fig4`), so it is
    not compared (validator warning expected).
  - `fig4_rigid_after` (datum `q_rigid_after_fig4`): the solid curve at t = 0.05-0.7 (beyond 0.7 it
    merges with the dashed curve near q = 0). Compared with Eq. 31 as printed (`cmp_fig4_eq31`, no
    p0: about 0.38 at t = 0+, not the drawn 9) and with the variant that restores p0
    (`cmp_fig4_eq31_p0`, lambda_q and lambda_p from beta_1 by Eq. 18). This settles nothing in the
    existing questions but raises q_eq31_missing_p0.
  - `fig4_windkessel` (datum `q_windkessel_fig4`): the dashed curve at t = 0.1-0.7 (at t < 0.1 it
    is too steep and leaves the plot box at the bottom); between dashes the value is joined across
    the gap. Its windkessel time-scales are not stated (q_fig4_parameters), so no run; recorded so
    a later model can be compared with it (validator warning expected).
