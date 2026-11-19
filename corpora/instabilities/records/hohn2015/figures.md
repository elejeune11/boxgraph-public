# Figures of hohn2015

Every reading is `mode: code` with its own reading code in `figures/`. The first pass read at 110 dpi
because the page-render and figure-check commands were refused then (q_figure_resolution); its readings
are kept unchanged. The second pass (2026-11-19) could render and check, and added high-resolution
readings of the same panels (ids ending `_hd`) and the two computed-profile panels of Fig. 4(d, e). Every
second-pass reading was checked with `boxgraph figure check` and its overlay inspected: the marks sit on
the intended line or markers.

## Read

- **Fig. 2(a)** e/e0 against t, red line of the representative embryo (measured):
  `fig2a_red` (110 dpi, every 5 min; datum `e_ratio_fig2a`) and `fig2a_red_hd` (1100 dpi, every minute
  t = -16 to 13 min, the red line's whole span; datum `e_ratio_fig2a_hd`). Shared code `_fig2.py`:
  box from its neutral lines, x ticks every 10 min mirrored top/bottom, y ticks 0.2-1.2 mirrored on both
  sides; misfit at 1100 dpi x 0.11 px, y 0.00 px. Value = middle of the red pixels' vertical extent in a
  narrow column band; interval = that extent + 1 px + misfit (wide where the line is steep, t = -1 to 1).
  e/e0 = 0.999 at t = -10 min, consistent with the caption's normalization at t approx -10 min.
- **Fig. 2(b)** A/A0, red line with open circles (measured): `fig2b_red` and `fig2b_red_hd`
  (t = -26 to 20 min; data `area_ratio_fig2b`, `area_ratio_fig2b_hd`). y calibrated from the top box line
  (level with 1.5) and the ticks 1.0, 0.5; misfit x 0.29 px, y 0.67 px at 1100 dpi. The open circles
  (times of the traced shapes) lie on the line and widen the interval where they sit; they are not read
  separately.
- **Fig. 2(c)** kappa*, red line (measured): `fig2c_red` and `fig2c_red_hd` (t = -25 to 19 min; data
  `kappa_star_fig2c`, `kappa_star_fig2c_hd`). y ticks every 0.02 um^-1 from either side and the bottom box
  line as -0.2; misfit x 0.21 px, y 1.82 px at 1100 dpi.
- **Fig. 4(d)** computed meridional stretch f_s against s/R (predicted by the unrunnable shell model):
  `fig4d_uncontracted` (thick line, purse-string legend icon; datum `fs_uncontracted_fig4d`) and
  `fig4d_contracted` (thin line, mushroom icon; datum `fs_contracted_fig4d`), 1800 dpi, s/R = 0.1 to 3.1
  every 0.1. Code `_fig4.py`: the axes are the row/column with most black (the thick curve covers parts
  of the x axis); x ticks every pi/8 from the y axis (labels pi/2, pi), indexed by spacing because some are
  hidden under the curves (4 found, misfit 2.2 px); the x axis is level with the label 1, y ticks every
  0.05 (8 found, misfit 1.5 px). Thick and thin lines are separated by the distance transform; the legend
  is removed from the image before reading. Where the thin line runs under the thick one (s/R >= 2.1) it
  is read as the thick line's extent. Left out: s/R = 1.6 on the thick line (the thin line's vertical
  jump at pi/2 joins it in the column band).
- **Fig. 4(e)** computed kappa_s R against s/R (predicted): `fig4e_uncontracted` (thick dashed line,
  blue and red; datum `kappa_uncontracted_fig4e`) and `fig4e_contracted` (thin solid line, blue and red;
  datum `kappa_contracted_fig4e`), 1800 dpi. Same code; 7 x ticks found (misfit 0.42 px), y ticks every 2.5
  with the x axis as 0 (6 found, misfit 0.36 px). In a dash gap the dashed line is interpolated between
  neighbouring dashes. Left out: the columns of vertical jumps (s/R = 1.3 and 1.6 on the dashed line,
  1.3 and 2.9 on the thin line, where two runs share the band). The red parts below about -9 lie past the
  end of the drawn y axis and rest on extending its calibration. The jump positions bound the bend region:
  1.32-1.57 (uncontracted) and 0.97-1.57 (contracted), which do not match the printed lambda approx
  0.1 pi R (new question q_fig4e_bend_width); the contracted posterior f_s of Fig. 4(d), 0.713-0.719,
  is near r_p/R approx 0.7. These curves are the fullest numerical output of the shell model in the
  paper, the natural target for haas2015/haas2021's fuller versions.
- **Fig. S3** per-embryo area change before expansion (measured) and the drawn median: `figS3_points`,
  `figS3_median` (110 dpi) and `figS3_points_hd`, `figS3_median_hd` (1000 dpi; data
  `area_change_points_figS3_hd`, `area_change_median_figS3_hd`). Calibration from the zero line, the top
  box line (20) and the ticks 10, -10, -20 (misfit at the 0.5 px floor). At 1000 dpi one marker is partly
  covered by its neighbour; its centre is bounded between the two positions its visible part allows. The
  median line is broken by markers drawn over it, so its rows are found by dark-pixel count rather than
  one unbroken run. Read values: -19.9, -15.9, -11.8, -10.2, -10.0, -9.4, -9.4, -9.2, +0.9, +14.8%;
  median line -9.75% [-9.98, -9.52]. The median of the markers is compared with the line
  (`cmp_median_figS3`, `cmp_median_figS3_hd`, consistency). This bears on q_area_reference_time: two of
  ten embryos increase, and the 'approx 10%' is the median.

No reading has a run or comparison against a model of this record other than the S3 median: the only
model that predicts the Fig. 2 and Fig. 4 curves (shell_inversion) is not runnable here
(q_shell_not_rerun). They are recorded as validation targets for haas2015 and haas2021.

## Left out

- Fig. 1: micrographs, schematics and 3D renderings; the curvature colour bar of 1(h) colours traced
  contours, which give no readable values.
- Fig. 2: the other nine embryos' lines (blue, cyan and green shades that cross and cannot be told
  apart, and the paper does not say which line is which embryo), the grey guide band of (a) (a drawn
  guide labelled '5x speed-up', not data), and the traced outlines of (b).
- Fig. 3: sketches of the model geometry and intrinsic properties, with symbolic axes only (pi R/2, pi R).
- Fig. 4(a-c, f-i), S1, S2: shapes and outlines without axes; the standard-deviation bars of (f, h) and
  the grey bands of (g, i) have no scale (q_fig4_shapes_no_axes).
