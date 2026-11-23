# Figures of cao2017: what was read and what was left out

All readings are `mode: code`: the build renders the crop and runs the record's own code in
`figures/` on it. Four shared files do the work:

- `_panel.py` reads the vector line plots (Figs. 4A-C, 5A, S4, S5). It finds the black frame and the tick
  marks (outward or inward), matches them to the printed labels, and fits a line. Where a corner tick is
  covered, a frame line standing at a labelled value is used. Curves are traced by nearest colour.
- `_raster_bars.py` reads Fig. 5D.
- `_s7.py` reads Fig. S7.
- `_fig3b.py` and `_fig3d.py` read Fig. 3B and Fig. 3D.

Misfit is the largest residual of the tick fit, in pixels at the reading's dpi. Every reading was checked
with `boxgraph figure check`, and its magenta marks sit on the curve, marker or bar meant.

## Main text

- **Fig. 1, Fig. 2**: left out. These are drawings (flowchart, schematics) with no values.
- **Fig. 3A**: left out. Simulation snapshots and a schematic; no axes.
- **Fig. 3B**: read as `fig3b_weak` (green, 18 markers), `fig3b_mid` (red, 10) and `fig3b_strong` (blue, 3).
  These are the DFN results; the markers were counted by eye and the code finds all of them. Calibration:
  - x uses the side frame lines at the printed 0.0 and 7.5, plus the inward ticks 2.5 and 5.0 (4 marks,
    misfit 0.5 px at 2400 dpi).
  - y uses the frames at 1 and 1.3 plus the 1.15 tick (3 marks, misfit 1.0 px). The bottom frame is covered by
    the blue line; its centre is taken from its visible lower edge.
  - The fit lines of Eq. 1 are not read. The markers sit on them, and the fit's n and sigma_c are not given
    (q_eq1_fit_fig3b).
  - The reading shows the DFN densities reach only about 1.27, while Eq. 1 with its printed factor 5 saturates
    at 6. So a fit of Eq. 1 to Fig. 3B can only use its low-stress foot, as q_eq1_fit_fig3b says. The reading
    does not settle the fit.
  - Origin `predicted` (a simulation result); no model in the record can rerun the DFN (q_dfn_not_runnable).
- **Fig. 3C**: left out. Micrographs.
- **Fig. 3D**: read as `fig3d_box`. These are measured box plots (soft, stiff, soft-weld; adapted from
  ref. 16 = baker2015), origin `measured`.
  - Value: the median line. Error bar: the whisker caps (error_bars `unstated`; the legend does not say what
    boxes and whiskers show). The quartiles are in each value's note.
  - The raster is blurred: lines are found as profile peaks beside the box centre. y calibration uses 4 ticks,
    misfit 2.3 px at 2400 dpi.
  - No model in the record predicts it; it is recorded for baker2015 and later models.
- **Fig. 4A**: read as `fig4a_E25`, `fig4a_E75`, `fig4a_E125` (blue, red, green) at 24 FA sizes from 0.5 to
  12 µm. Calibration: 7 x ticks and 4 y ticks, misfit 1.0 / 1.3 px at 1200 dpi. Legend swatches are blanked.
  - The calibrated red peak (about 7.9 kPa) is lower than the old eye read (8.4), and the tails differ from
    the eye reads by up to about 1.5 kPa (red) and 2.4 kPa (green) at 12 µm; the eye reads were too high
    beyond about 6 µm. The eye-read data are kept as they were.
  - The 7.5 and 12.5 kPa curves feed `run_rst_fig4a_calibrated` (below).
- **Fig. 4B**: read as `fig4b_L03`, `fig4b_L1`, `fig4b_L3`, `fig4b_L10` (blue, red, green, magenta) at 11
  positions. The 1D integrin force profiles come from the coarse-grained model. Calibration uses 5 ticks per
  axis (the unlabelled ticks halfway between the labelled ones), misfit 2.5 / 0.5 px at 1800 dpi.
  - Recorded, not compared: the COMSOL model is not runnable (q_coarse_not_runnable).
- **Fig. 4C**: read as `fig4c_n0` (blue) and `fig4c_n8` (red) at the same 24 sizes as Fig. 4A. Misfit 1.4 /
  0.6 px.
  - **Settles q_fig4a_fig4c**: `cmp_fig4a_fig4c_calibrated` compares Fig. 4A red with Fig. 4C blue. All 24
    points are reproduced within the reading intervals. The two panels show the same curve; the earlier
    difference was an eye-reading error (q_fig4a_fig4c_calibrated).
  - The n = 8 curve has no model to compare with.
- **Fig. 4D, 4E**: left out. These are schematics. Fig. 4E's growth-rate curve is a generic shape with no
  values on its axes.
- **Fig. 5A**: read as `fig5a_n0`, `fig5a_n2`, `fig5a_n4`, `fig5a_n8`, and `fig5a_n0_at4a` (the n = 0 curve at
  7.5 and 12.5 kPa). Calibration: 5 x ticks and 7 y ticks, misfit 0.6 / 0.5 px at 1200 dpi.
  - The four curves overlap at the onset (about 3-4 kPa) and above about 15 kPa. Each curve is read only where
    it is not drawn under another (n = 8, on top, is read to 20 kPa).
  - `cmp_rst_fig5a_calibrated` runs `stable_size_vs_modulus` on the calibrated Fig. 4A curves. With the
    record's middle nucleus modulus (7.5 kPa) it is **not reproduced** at both moduli. A nucleus modulus near
    the top of the printed 5-10 kPa range brings both close (q_rst_calibrated_En). This sharpens q_En_range;
    it does not settle it.
  - The eye-read comparisons cmp_rst_E75/E125 are kept.
  - At 2.5 kPa the Fig. 4A curve never reaches sigma* (no stable FA), which agrees with Fig. 5A having no
    n = 0 FA below about 2.8 kPa. That is not compared, since there is no value to compare.
  - The n = 2, 4, 8 curves have no runnable model (fibre recruitment needs sigma_c and the unit of n,
    q_eq1_sigma_c_n).
- **Fig. 5B**: left out. This is a colour heat map (FA band size over E_ECM and n). Reading it would mean
  inverting a jet colour map with a colour bar of three labels. The same model output is read more precisely
  from the curves of Fig. 5A.
- **Fig. 5C**: left out. Micrographs.
- **Fig. 5D**: read as `fig5d_area`. These are the measured average FA areas (adapted from ref. 16), four bars
  (x = 1 hydrogel soft, 2 hydrogel stiff, 3 fibres soft, 4 fibres stiff), origin `measured`.
  - A blurred raster with grey axes. Bar tops are taken at the half-way crossing of the edge; 6 ticks, misfit
    2.6 px at 1600 dpi.
  - Only the upper error bars are drawn. The lower ends are mirrored, and what the bars show is not stated
    (`unstated`).
  - `cmp_fig5d_figS7_calibrated` normalizes the four bars by the stiff-fibre bar (`normalize_by_reference`).
    The result is reproduced against Fig. S7's experimental bars at all four conditions, within their error
    bars. The ratios run a few per cent above the S7 bars, which is not significant at this precision.

## Supporting Information

- **Fig. S1, S2, S3**: left out. Snapshots of the network coloured by strain energy and force (these show
  fields, not values along an axis), and schematics.
- **Fig. S4**: read as `figS4_density`, the normalized ligand density against E_ECM (rFA = 8 µm, n = 8), at 0-19
  kPa.
  - Calibration: the inward ticks at 2 and 4 and at 5, 10 and 15. The frame lines stand at x = 0 and 20 and
    y = 0; the tick at 6 is covered by the curve. Misfit 0.9 / 0.5 px at 1200 dpi.
  - The dashed line at 1 is a reference and is not read; at 20 kPa the curve runs under it and is not read.
  - No runnable model gives it (q_eq1_ecm_dependence, q_eq1_sigma_c_n).
- **Fig. S5A**: read as `figS5A_blue`, `figS5A_red`, `figS5A_green` (L << 4Lc, L ~ 4Lc, L >> 4Lc; reprinted
  from ref. 24).
  - Here y = 0 is a dashed line above the bottom frame, so y is calibrated on the labelled ticks 0.2 to 0.8
    only. x uses 0.2-0.8 plus the frames at 0 and 1. Misfit 0.5 / 0.9 px at 2000 dpi.
  - The blue line runs under the top frame beyond x/L = 0.6 and is not read there. The green line lies on the
    dashed zero line between 0.1 and 0.6 and is not read there.
  - No numerical L or Lc is given for the curves, so no model run.
- **Fig. S5B**: read as `figS5B_up` (blue, plaque) and `figS5B_us` (red, ECM), for an FA 16 Lc long.
  - Calibration: inward ticks plus the frames at x = 0 and 16 and y = 0. Misfit 0.7 / 1.0 px at 1800 dpi.
  - The red curve is drawn over the blue from about 1.5 to 11.5 Lc, so the blue is read only beyond 12.5 Lc.
  - Not compared: the stiffness ratios are not given (q_1d_stiffnesses).
- **Fig. S5C**: left out. Its axes carry no values (only "~4Lc" and "FA Size (L)").
- **Fig. S5D**: left out. A drawing.
- **Fig. S5E**: read as `figS5E_Lc` at 13 ligand densities from 2 to 90 per µm. Calibration: inward ticks plus
  the frames at x = 0, 100 and y = 0; misfit 0.5 / 0.6 px at 2000 dpi.
  - Densities 60 and 80 are left out, where the curve lies on the inward x ticks.
  - `cmp_Lc_curve_figS5E` sweeps `shear_lag_length` (Lc proportional to 1/phi_i, scaled from the printed
    0.436 µm at 1 per µm) over the curve. All 13 points are **reproduced**: the plotted curve follows the printed
    formula's 1/phi_i scaling.
- **Fig. S5F**: read as `figS5F_keff` (keff/kp against ligand density, FA of 0.1 µm) at 16 densities.
  Calibration: inward ticks 1, 2 and 20-80 plus the frames; misfit 0.9 / 0.7 px.
  - Not compared: kp, ks and kc are not given (q_keff_1d_unrun).
  - The reading now gives the peak's height and position. With the printed Lc these are the two numbers
    q_keff_1d_unrun asks for to test the printed keff formula. Fitting the one unknown stiffness ratio is left
    to a later pass.
- **Fig. S6**: left out. 3D surface plots in a colour map; their values cannot be read along an axis.
- **Fig. S7**: read as `figS7_exp` (the solid bars, ref. 16, with error bars) and `figS7_model` (the hatched
  bars), x = 1 to 4 as Fig. 5D.
  - Calibration: 7 inward ticks (0 to 3 by 0.5), misfit 1.3 px at 1200 dpi. Each bar is taken at the centre of
    its top outline.
  - Both stiff fibrous bars read 1.000, as the normalization requires: a check on the calibration.
  - Error bars: the upper cap is read on every experimental bar. The lower cap is read where it is drawn over a
    grey bar, and mirrored inside a black bar (`unstated`).
  - `cmp_figS7_model_vs_exp` (validation) is reproduced at hydrogel soft and fibrous soft (and at fibrous stiff
    by construction). It is only **close** at the stiff hydrogel: the model bar sits at 1, below the
    measured bar's error bar (q_figS7_hydrogel_stiff).
- **Table S1**: values entered earlier (data.yaml); no figure.
