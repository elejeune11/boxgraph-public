# Figures of spaan1981

Figs. 5 and 6 are read by the record's own code (`figures/`), rendered at 600 dpi. An earlier pass
read no figure, because the rendering tools were not available then. Its notes below on Figs. 1-4
and 7 still hold.

- **Fig. 1, 2, 3**: drawings (the preparation, the principle of the pump, the electrical analog).
  They hold no values. Left out.
- **Fig. 4** (panels A-D): single phasic recordings (LV pressure, left main pressure, CBF) of one
  dog at four stenosis grades. These are time traces of a few beats, not data points. The one number
  the paper takes from them (the 0.13 ml area of panel A) is printed and recorded from the text.
  Left out.
- **Fig. 5**: measured p_lc vs q_c in one dog at four P_lc. Read as `fig5_plc65` (filled squares,
  7 points), `fig5_plc90` (filled down-pointing triangles, 8; the experiment of Fig. 4),
  `fig5_plc125` (filled circles, 10) and `fig5_plc155` (filled up-pointing triangles, 9). One more,
  `fig5_unclassified`, is a round marker cut by the x axis at q_c of about 2. Its square or circle
  shape cannot be judged, so it is recorded with no P_lc.
  - **Calibration:** from the inward tick marks. The bottom axis's ticks are matched to 0.5, 1.0
    and 1.5 (misfit 2.0 px, where 1 px = 0.0007 ml/s). The left axis's ticks are matched to 10-50
    (misfit 2.7 px, where 1 px = 0.033 mm Hg).
  - **Finding the markers:** the fitted lines are removed by a 9 px opening. Each marker is
    classified by matching it against the figure's own legend symbols as templates. Square and
    circle are then told apart by the ink in the box corners. Two overlapping markers (a triangle
    and a circle near q_c = 0.47) are separated into two matches.
  - **Intervals:** about ±0.16 mm Hg; ±0.26 for the two overlapping markers.
  - **Checks:** all overlays checked.
  - **Not compared:** no run uses these points. Eq. 2 needs each curve's R_a and p_im, which are
    not printed (see q_fig5_fits_not_rerun).
  - **Not read:** the four fitted lines. They are fits to these points, with no printed parameters,
    and their ends merge near the y axis.
- **Fig. 6**: measured R_a vs R_c, 25 points from six dogs (the printed n = 25). The readings are
  `fig6_open_triangle` (4), `fig6_filled_circle` (8, including two touching markers split at
  R_c ≈ 48), `fig6_filled_square` (4, the dog of Fig. 5), `fig6_open_circle` (3), `fig6_open_square`
  (4) and `fig6_filled_triangle` (2).
  - **Calibration:** from the inward tick marks. The bottom axis is matched to 20-120 (misfit
    5.4 px, from irregularly drawn ticks, where 1 px = 0.050). The left axis is matched to 20-60
    (misfit 2.5 px).
  - **Classification:** markers are classified by fill, hollowness and taper. A marker inside a
    ring is excluded from the measured points.
  - **Intervals:** ±0.2-0.4 mm Hg s/ml.
  - **Comparisons:** each dog's points are compared (fit_quality) with the printed regression
    R_a = 0.63 R_c - 12.9, run at their R_c.
  - **Waterfall lines:** the three lines of the 20-layer waterfall model are read as
    `fig6_wf_open_triangle`, `fig6_wf_open_square` and `fig6_wf_filled_square`. Each gives two
    points: the ring centre and the traced free end of the line. These are its calculated points at
    P_lc = 65 and 155 mm Hg; which end is which is not stated. They are recorded as predicted data.
    They are not compared, because that model is not runnable.
  - **Checks:** all overlays checked.
- **Fig. 7**: a single recording of LV and left main pressure decaying after clamping, with the
  authors' drawn estimate (broken line). It is one trace, and its two RC times (0.2 s and 3 s) are
  printed in the caption and text and recorded from there. Left out.

## Open questions the figures bear on

- **q_figures_not_read:** both figures are now read (q_fig6_points_read, q_fig5_fits_not_rerun).
- **q_ra_63_percent:** the plotted R_c run from about 30 to about 138, wider than the range used
  there (q_fig6_points_read).
- **q_fig7_resistances_source:** no Fig. 6 point lies near R_c = 100, R_a = 65, so the Fig. 7
  resistances are not one of the plotted points (q_fig7_dog_not_in_fig6).
