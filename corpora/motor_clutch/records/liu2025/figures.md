# Figures of liu2025: what was read and what was left out

Two passes. The first pass read model curves at 110 dpi with `figures/_fig.py` (and `_ed5.py`);
those readings are kept unchanged. The second pass renders each panel at 1000 dpi with
`pdftoppm` and reads it with `figures/_hd.py`: axes are calibrated from the tick marks found in
the image (the long ticks of each axis, matched by position to the printed labels; least squares,
misfit = largest residual, at least 0.5 px), and every interval also carries the size of a pixel of
the raster the figure was printed from, measured from the image (`source_px`: about 1.3 px for the
article's own figures, 3-8 px for the web images of the Extended Data figures, which are coarse).
Symbols are found by their fill colour (blobs joined where a curve or another symbol cuts them;
centroid, or centre of the joined box) or, on the sharp article figures, by matching their dark
outline (`symbols`); bars by the top edge of their colour; boxes by their filled rectangle.
Calibration misfits were 0.5-0.85 px on every second-pass axis except the x axis of Extended Data
Fig. 5 (2 px, a 10^6 tick at the crop edge). Each reading was checked with `boxgraph figure check`
and its overlay (`figwork/<id>.png`, not committed).

## Main text

- **Fig. 1**: schematic of the model; no values. Left out.
- **Fig. 2(a)**: stability diagram (kon against kc) with the two cell-type points; its axis
  parameters other than those of the cusp case are not all printed. Left out (as before).
- **Fig. 2(b)**: talin WT ensemble force-extension curves; the talin model is not runnable
  (q_talin_model). Left out.
- **Fig. 2(c)**: model curves read in the first pass (`fig2c_linear_kd`, `fig2c_linear_wt`).
  Second pass: the measured points, `fig2c_data_wt` (6 pink circles) and `fig2c_data_kd`
  (6 green triangles), outline-matched at 1000 dpi; x on the decades 10^2-10^6 left of the axis
  break, y on 0/60/120/180; misfit 0.5 px. Compared with the fitted linear WT / KD models
  (`cmp_*_data_fig2c`, fit_quality). Two triangles lie partly under circles; their intervals
  are widened by the hidden share of their outline.
- **Fig. 2(d)**: model curves (first pass). Second pass: `fig2d_data_wt` (6 circles, the last
  one right of the axis break, read at the 10^11 tick, the only labelled tick there; it sits
  44 px left of it, on the flat plateau of the curve) and `fig2d_data_kd` (5 triangles);
  fit_quality comparisons.
- **Fig. 3(a)**: `fig3a_data_fn100` (5 of 6 green triangles), `fig3a_data_fn10` (6 circles, the
  same WT data as Fig. 2c), `fig3a_data_fn1` (4 of 6 blue triangles); fill blobs, misfit 0.5 px.
  Not read: the 1 ug/ml triangle at 2.4 kPa (drawn semi-transparently over two other symbols,
  its fill colour changed) and the symbols of the 600 Pa and 2.4 kPa clusters hidden under the
  others. The model curves (linear WT and talin WT fits per fibronectin density) are left out:
  their fitted parameters are only plotted (Fig. 3c is for the talin WT model), so no model here
  produces them.
- **Fig. 3(b)**: `fig3b_data_fn100` (6), `fig3b_data_fn10` (5), `fig3b_data_fn1` (4) traction
  points of talin-deficient cells; the hidden members of the 600 Pa cluster are not read. Model
  curves left out (linear KD fits with unprinted parameters).
- **Fig. 3(c)**: `fig3c_kon`, `fig3c_r`, `fig3c_sm`: the fitted talin WT parameters at 1, 10,
  100 ug/ml, each series calibrated on its own y axis (left log axis for k0on, first right log
  axis for r, second right linear axis for sigma_m); dots by their colour, opened to cut away
  the connecting lines. At 10 ug/ml they differ from Table T1's talin WT values
  (q_fig3c_vs_tableT1). They are talin WT parameters, so they do not supply the linear WT fit at
  1 ug/ml needed for the Extended Data Fig. 3 thresholds (q_ed3_kc_threshold stays open).
- **Fig. 3(d)**: micrograph. Left out.
- **Fig. 3(e)**: `fig3e_nih3t3`, `fig3e_hela`: the mean +- s.e.m. boxes of myosin-stack density
  at 1, 10, 100 ug/ml; value at the box middle, interval the box. The s.d. whiskers are not read:
  the individual cells' points pile up on their caps and the caps could not be found reliably.
  The individual points are not read (overlapping clusters).
- **Fig. 3(f)**: violin plots of stack areas with small mean +- s.e.m. boxes and median circles
  drawn inside the violins. Left out in this pass: the boxes are a few pixels tall, drawn over
  the violins' outlines in nearly the same colour, and could not be isolated reliably.
- **Fig. 4(a)**: master-equation (Eq. I1) time courses of the talin WT model with vinculin; not
  runnable here. Left out (curves only; no measured data).
- **Fig. 4(b)**: NA area and talin/vinculin intensities (about 60 points per series with s.e.m.
  bars, each symbol overlapping its neighbours and the other series) with the talin WT model.
  Left out: the symbols are not separable as points.
- **Fig. 4(c)**: `fig4c_data_vd1` (6 VD1 triangles), `fig4c_data_vko` (the vinculin-KO point);
  the WT circles are the Fig. 2c data and are read there. WT-2 model curves left out (WT-2 model
  not runnable here).
- **Fig. 4(d)**: `fig4d_data_vko` (the vinculin-KO point at the 10^11 tick); WT circles as
  Fig. 2d.
- **Fig. 4(e)**: `fig4e_bars`, the four predicted loading rates (talin WT model); not compared
  (q_unrunnable_figure_results).
- **Fig. 4(f)**: `fig4f_exp` (measured, 4 bars with their 95% CI error bars, read down inside
  the bars), `fig4f_theory_300`, `_200`, `_100` (predicted bars); misfit 0.85 px.
- **Fig. 4(g)**: `fig4g_novd1`, `fig4g_vd1`: the four yellow markers on the talin
  force-extension traces at 5 and 10 pN (differences 36 and 105 nm, against the text's "~40"
  and "~110"; q_fig4g_dx). The noisy single-molecule traces themselves are not read.
- **Fig. 5(a,b,d)**: three-dimensional renderings of the bistability regions; no readable axes
  for values. Left out.
- **Fig. 5(c)**: `fig5c_sn1` (red, 1st saddle-node point) and `fig5c_sn2` (blue, 2nd), read as
  sigma_m along the row of each E (an E-indexed reading); compared with the new model
  `saddle_nodes_sigma_m` (local extremes of sigma_m(v) of Eq. 8). The plotted boundaries lie
  about 3% above the computed ones (q_fig5c_boundaries).
- **Fig. 5(e,f)**: stability diagrams in (kc, sigma_m) with unprinted parameter sets. Left out.
- **Fig. 6**: single stochastic trajectories and schematics. Left out.

## Extended Data

- **Extended Data Fig. 1**: geometric construction (schematic). Left out.
- **Extended Data Fig. 2(a,b)**: the same measured points as Fig. 2c,d (read there) with WT-2
  model curves (not runnable). **(c)**: the same data plotted as traction against flow. **(d)**:
  schematic. Left out.
- **Extended Data Fig. 3**: linear WT curves for several kc with the fibronectin 1 ug/ml fit
  parameters, which are not printed (q_ed3_kc_threshold), and (c) transients. Left out.
- **Extended Data Fig. 4(a,b)**: `ed4a_maxwell`, `ed4b_maxwell` (predicted bars at
  xi_s = 0.1-100 pN s/nm, not compared), `ed4b_exp` (measured flow on DOPC, DPPC, glass, with
  s.d. error bars; the error bars over the dark-blue bar needed a dark mask of any hue). The
  Kelvin-Voigt bar has no numeric x (it is the elastic limit) and is not read. **(c)**: NA area
  time courses of the Maxwell master equation (not modelled). Left out.
- **Extended Data Fig. 5(a,b)**: model curves read in the first pass. Second pass: the measured
  points `ed5a_data_0uM`, `_15uM`, `_50uM` and `ed5b_data_0uM`, `_15uM`, `_50uM`, from a coarse
  web raster (7.6 px per source pixel; fill blobs). Not read: the 600 Pa cluster in both panels
  (the three symbols lie on top of each other), and in (b) the 15 uM triangle at 2.4 kPa hidden
  under a circle. fit_quality comparisons with the linear KD / WT models at the fitted sigma_m.
- **Extended Data Figs. 6, 7 (a, b, d)**: `ed6a_plateau`, `ed6b_plateau`, `ed6d_plateau`,
  `ed7a_plateau`, `ed7b_plateau`, `ed7d_plateau`: the steady values reached by the
  master-equation time courses at t = 55 s, one per E-labelled curve (the overlapping curves of
  the three viscosities make one run; in (d) only the red and green curves, which have reached
  their plateau), indexed by E and compared with `steady_linear`. They settle that the linear WT
  ly is large and that S = pi R^2 (q_ed6_settles_ly_S). The transients themselves, (c) the
  p_on distributions and (e) the relaxation times are left out (time-dependent master equation
  not modelled).
- **Extended Data Fig. 8(a,b)**: micrographs and masks. Left out. **(c-e)**: per-cell NA area
  and intensity time courses, four cells, about 90 overlapping symbols per series with error
  bars; left out because the symbols are not separable as points.

## Supplementary Information

- **Fig. S1(a)**: `s1a_linear_kd` (green) and `s1a_linear_wt` (solid red, the lower of the two
  red lines at the top; the dotted talin WT line above it is not read): engaged-clutch density,
  compared with `steady_linear` n_on. **(b)**: `s1b_linear_kd`, `s1b_linear_wt` (solid red,
  searched below the 1.7 pN level so the dash-dotted unfolded-talin curve is excluded; not read
  where the two cross, 2-5 kPa): mean clutch tension, compared with F1. Vector figure, misfit
  0.5 px. This answers q_fig_S1_linear: both reproduce within a few percent.
- **Fig. S1(c,d)**: WT-2 model curves; not runnable here. Left out.
- **Fig. S2**: micrograph. **Fig. S5**: schematic. Left out.
- **Fig. S3(a)**: Ie against eccentricity; Ie is checked through Eqs. A11/A13 and Ie(0) = 1
  instead (as before).
- **Fig. S4**: `s4_curve` (the red Eq. 4 fit, read at 9 forces between the symbols; y log
  0.1/1/10, x 0/15/30/45; vector, 1200 dpi, misfit 0.5 px) and `s4_data` (the 9 digitized
  dissociation rates of ref. 10 with their s.e.m. bars; outline-matched circles). Compared with
  the new model `koff_eq4` on the Table T1 values: the curve is reproduced with kBT = 4.28 pN nm
  and not with 4.11 (q_figS4_kT).
- **Fig. S6**: special functions. Left out.
