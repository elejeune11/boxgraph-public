# Figures of hong2009

The letter has four figures. Only Fig. 3 plots values; it has no measured data. The paper's only
measurements (epsilon_exp = 0.35, eta_exp = 2.0-3.7) are printed in the text and taken from cited work.

- Fig. 1: a photograph of a crease on a starch gel (Liang Fen); no values.
- Fig. 2: sketch of the reference, homogeneous and creased states; no values.
- Fig. 3: read (`fig3_energy`, datum `fig3_energy_curve`, origin `predicted`): the single blue
  finite-element curve U/(mu L^2) against the applied strain epsilon, at epsilon = 0.20 to 0.35 in steps
  of 0.01. Read with code at 1000 dpi (`figures/fig3_energy.py`). The axes are calibrated from the nine
  x ticks (0.2-0.36) and nine y ticks (0-0.8) on the plot frame, each fitted with a straight line. The
  largest misfit is 5.1e-5 in x and 3.4e-4 in y. The 95% intervals are about ±0.002-0.004 and come from
  line width plus misfit. The overlay (`figwork/fig3_energy.png`) puts every mark on the curve. The curve
  ends near epsilon = 0.351 with f about 0.02, so nothing past 0.35 is read. Run `run_fig3_zero` finds
  the zero of this curve, and it is compared with the printed epsilon_c = 0.35 (`cmp_epsc_fig3`,
  `cmp_epsc_fig3_approx`) and the experimental 0.35 (`cmp_epsc_fig3_exp`). The curve itself is not
  compared with a run because the ABAQUS model cannot be rerun (`q_fe_not_rerun`), which is why the
  validator warns that the curve is never compared.
  On `q_zero_extrapolation`, the figure does not settle it. The read slope steepens towards the end
  (about -6.5 per unit strain between 0.33 and 0.34, about -8.6 between 0.34 and 0.35). So the
  straight-line zero from the last two points is an upper bound on where a steepening curve would
  reach zero, but the plotted curve stops before f = 0 and the figure gives no zero to read directly.
- Fig. 4: sketch of the generalized plane-strain mapping (reference, current and intermediate unit
  cubes); no values.
