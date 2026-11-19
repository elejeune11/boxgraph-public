# Figures of haas2015

Every reading is `mode: code` with its own reading code in `figures/`. Each was checked with
`boxgraph figure check` on the render at the reading's dpi; the overlays are in `figwork/<id>.png`.
The paper plots no measured data: its only experimental images are the micrographs of Fig. 1, so
every reading below is a model result.

## Read

- **Fig. 2(c)** (`fig2c_points`): the green + markers, the paper's numerical F against f.
  The markers sit on the solid line of (2.9), so only the markers are read; the line is the
  closed form itself. Compared with `phi_eq29` and the reconstructed `lame_plane_numeric`.
- **Fig. 3(g)** (`fig3g`, `fig3g_curve`): the solid curve K / sin^1/2 Theta against
  Lambda = lambda/delta. Not read at Lambda = 2.44 (the dashed vertical line) or below Lambda = 1
  (the curve leaves the box). Compared with `curvature_eq33` and `curvature_b14_numeric`.
- **Fig. 3(h)** (`fig3h_i`, `fig3h_i_curve`, `fig3h_c`, `fig3h_c_line`): the thick solid curve
  Delta beta^(i)/cos Theta and the dashed line Delta beta^(c). Compared with `rotation_b18`,
  `rotation_b16_numeric` and `rotation_contraction_eq35`.
- **Fig. 5** (`fig5_critical_branch`, `fig5_critical_point`; data `k_critical_branch_fig5`,
  `critical_point_fig5`): the orange critical branch (lambda = lambda*) at 12 values of d/R
  (not near the dot, 0.53 < d/R < 0.63), and the orange critical-point dot (its centre, both
  coordinates). Calibrated on the y axis line and 15 x ticks (0.1 per tick; x misfit 0.0009) and
  on 10 y ticks, three labelled 30, 20, 10 (y misfit 0.003). The curve is found by its flat colour
  (255, 89, 0); the leader line and the dot are left out. 1200 dpi. No model in the record
  produces it (`shell_bifurcation` is not runnable, q_shell_not_rerun). The same code reads the
  branch again at the 11 positions Fig. 7(c) also shows (`fig5_critical_branch_at7c`, datum
  `k_critical_branch_fig5_at7c`); that reading is compared with Fig. 7(c)'s drawing of the branch.
- **Fig. 7(b)** (`fig7b_upper`, `fig7b_lower`; data `kappa_upper_fig7b`, `kappa_lower_fig7b`):
  the two black branches of the (k, kappa) diagram, kappa/(G R) against kR, the upper labelled
  lambda > lambda* and the lower lambda < lambda*. Read at kR = 6-9 and 12-17 (upper) or 12-19
  (lower): below kR = 6 the two branches run together, and between 9.3 and 11.2 the upper one
  folds (S shape, three runs per column). Calibrated on the y axis and 8 x ticks (2.5 per tick,
  x misfit 0.006 in kR) and on 6 y ticks, three labelled 3, 2, 1 (y misfit below 0.001). 1200 dpi.
  The branches are labelled only by an inequality on lambda, so no run can reproduce them; they
  are recorded for a later model (haas2021) and carry no comparison.
- **Fig. 7(c)** (`fig7c_critical_branch`, `fig7c_critical_point`, `fig7c_spinodal`,
  `fig7c_metastable`): the orange critical branch at the x positions of the Fig. 5 reading (the
  last, d/R = 1.1, is above the crop and left out), the orange critical-point dot, the thick
  green boundary of the cross-hatched unstable region (the spinodal) at d/R = 0.3-0.8, and the
  thick blue outer boundary of the metastable band at d/R = 0.2-1.0. Calibrated on the y axis
  and 12 x ticks (0.1 per tick, x misfit 0.0011) and on 8 y ticks, two labelled 20, 10 (y misfit
  below 0.001, from the regularity of the tick grid). The green and blue curves are told from the
  hatching, crosses, arrows and words of the same colour by stroke thickness; where a black branch
  crosses them the gap is closed. Not read under the dot, at d/R = 0.55-0.6 on the green and blue
  curves, or at d/R = 0.8 on the blue one (two runs in the column). At d/R = 0.45 a cross touches
  the green curve and widens its interval. The critical branch is compared with Fig. 5's
  (`cmp_critical_branch_fig7c_fig5`, consistency); see q_fig7c_inputs.
- **Fig. 8** (`fig8_rp1`, `fig8_rp075`; data `critical_trajectory_rp1_fig8`,
  `critical_trajectory_rp075_fig8`): the two labelled trajectories of the critical point, k*R
  against lambda*/R as lambda_max varies: r_p = R (darkest, colour (0, 0, 153), labelled) and
  r_p = 0.75 R (lightest, colour (153, 153, 255), the colour of the colour bar's end labelled 0.75).
  Calibrated on the y axis and 10 x ticks (0.1 per tick, x misfit 0.0006) and on 6 y ticks, three
  labelled 30, 20, 10 (y misfit 0.002); the y axis is broken below 10, and only the part above the
  break is used. 1200 dpi. Not compared: no model in the record produces them. The two readings
  let the claim that contraction lowers k* and raises lambda* (q_shell_not_rerun) be seen at
  calibrated values, but the build gives it no verdict.

The tick label 2.44 of Fig. 3(g) is entered as a printed value (`L_min_fig3g`).

The readings of Figs. 2(c) and 3(g, h) were developed on scaled 110-dpi page images in an earlier
session (q_figure_tools); they are kept unchanged.

## Left out

- Fig. 1: micrographs and geometry sketches, no values.
- Fig. 2(a, b), Fig. 3(a-f), Fig. 4: sketches and computed shapes without axes.
- Fig. 5: the black and grey branches and the thin dashed k ~ d^1/2 lines. They are not labelled
  with their value of lambda, so no curve can be tied to its inputs. The green dashed spinodal and
  the thick green unstable parts of the branches share one colour and touch, so they cannot be told
  apart reliably. The spinodal is read in Fig. 7(c) instead.
- Fig. 6: sketches of the effective energy, with axes marked only as 0, beta/2, beta and no values.
- Fig. 7(a): sketches of fold topologies, without axis values.
- Fig. 7(c): the black branches (unlabelled, as in Fig. 5).
- Fig. 8: the four intermediate trajectories, whose r_p/R is shown only by a shade on the colour
  bar between the labelled ends 1 and 0.75; the dotted lines of constant lambda_max, which are
  unlabelled except for the orange lambda_max = pi R/2 line (it joins the ends of the trajectories
  and has no values of its own beyond theirs).
- Figs. 9, 10: mode shapes and geometry sketches without axis values.
