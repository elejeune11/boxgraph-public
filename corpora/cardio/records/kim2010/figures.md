# Figures of kim2010

Every reading below is a calibrated reading by the record's own code (`figures/*.py`), run by every
build on the page rendered at the stated dpi. Waveform panels share `figures/_wave.py`, Fig. 6 shares
`figures/_fig6.py`; their docstrings say how axes are calibrated and curves are followed. Each overlay
was checked with `boxgraph figure check` (files in `figwork/`, not committed).

Waveforms are results of the paper's 3D finite element simulations, which no model in this record can
run (question `q_3d_not_runnable`), so their data are recorded (origin `predicted`) without runs or
comparisons; a later record's model may predict them. Times are read every 0.05 s (0.015 s for the
0.3 s moderate-exercise cycle). Where two curves overlap, the interval covers the merged ink; where a
dashed or dotted curve has a gap, the value is interpolated between the ink on either side and the
interval spans both ends.

## Fig. 1 (p. 3, journal p. 3197)
- Left out: a schematic of the boundary conditions; the elastance sketch has no values on its axis.

## Fig. 2 (p. 8, journal p. 3202), 1600 dpi
Axes: y from the grey top gridline and the grey x axis (pressure panels: 138 and 68 mmHg) or from the
top gridline, the zero line and the bottom gridline (flow panels: three labels, misfit at most about
1 px); x from the grey y axis (0) and the tick at the right end of the x axis (1 s), checked against
the right end of the gridlines (misfit 0 px except H flow, 3.5 px).
- Pressure-volume loops: `f2_pv_lv_rest` (solid black, left ventricle at rest) and `f2_pv_lv_ex` (dashed
  black, left ventricle in exercise): the upper (ejection) branch of each loop at volumes 65-130 cc
  (x from the y axis, 0 cc, and the right-end tick, 150 cc). A loop is not a function of volume, so only
  this branch is read; the filling branch runs along the right ventricle's loops and the loops' vertical
  sides are not single valued. The right ventricle loops (grey solid and grey dashed) overlap each
  other along their whole length and are left out.
- D-Left vertebral pressure: `f2_D_p_rest` (solid), `f2_D_p_ex` (dashed).
- D-Left vertebral flow: `f2_D_q_rest`, `f2_D_q_ex`.
- C-Left carotid pressure: `f2_C_p_rest`, `f2_C_p_ex`; flow: `f2_C_q_rest`, `f2_C_q_ex`.
- B-Left subclavian pressure: `f2_B_p_rest`, `f2_B_p_ex`; flow: `f2_B_q_rest`, `f2_B_q_ex`.
- E-Right carotid pressure: `f2_E_p_rest`, `f2_E_p_ex`; flow: `f2_E_q_rest`, `f2_E_q_ex`.
- G-Right subclavian pressure: `f2_G_p_rest`, `f2_G_p_ex`; flow: `f2_G_q_rest`, `f2_G_q_ex`.
- H-Descending thoracic aorta pressure: `f2_H_p_rest`, `f2_H_p_ex`; flow: `f2_H_q_rest`, `f2_H_q_ex`.
- A-Aortic inlet pressure: `f2_A_p_rest`, `f2_A_p_ex`; flow: `f2_A_q_rest`, `f2_A_q_ex`. The flow panel's
  zero line is hidden under the curves, so its y axis uses the top and bottom gridlines only (580 and
  -20 cc/s). The exercise inflow lies under the rest curve on zero flow from about 0.38 to 0.49 s and
  from about 0.78 s to the end; those times are not read for `f2_A_q_ex`.
- The 3D rendering and the legend carry no values.
- What the figure settles: the exercise pressure curves of H and A stay below the 138 mmHg gridline,
  while the text gives 149 mmHg systolic pressure in light exercise (new question
  `q_fig2_systolic_exercise`); the panel titles swap left and right relative to the Table 2 note (new
  question `q_fig2_branch_labels`). The exercise curves repeat with a 0.5 s period, as Table 1's light
  exercise cycle says (the two plotted beats read alike within their intervals).

## Fig. 3 (p. 9, journal p. 3203), 1600 dpi
Axes are black here: y from the top line and the x axis (138 and 68 mmHg; flow 4.5, 5 or 2 and 0 cc/s),
x from the y axis and the end tick (0 and 1 s); the axis lines are removed before the curves are
followed.
- a-d LAD pressure: `f3_lad_p_rest`, `f3_lad_p_ex`; flow: `f3_lad_q_rest`, `f3_lad_q_ex`.
- e-h LCX pressure: `f3_lcx_p_rest`, `f3_lcx_p_ex`; flow: `f3_lcx_q_rest`, `f3_lcx_q_ex`.
- i-k RCA pressure: `f3_rca_p_rest`, `f3_rca_p_ex`; flow: `f3_rca_q_rest`, `f3_rca_q_ex`.
- The mean of each rest and exercise flow curve is printed in the text (p. 3201) and recorded as data;
  a time average of a read curve cannot be formed by a run in this record, so the curves are not
  compared with those means.
- The 3D rendering carries no values.

## Fig. 4 (p. 10) and Fig. 7 (p. 12)
- Left out: colour renderings of wall shear stress and of velocity magnitude on the 3D geometry; no
  values can be read from them.

## Fig. 5 (p. 11, journal p. 3205), 1600 dpi
Grey axes, two labels each (flow at rest 3 and 0, pressure at rest 130 and 60, flow in exercise 11 and 0,
pressure in exercise 130 and 0); x from 0 to 1 s at rest and 0 to 0.3 s in moderate exercise.
- LAD flow at rest: `f5_q_rest_normal` (solid, Normal) only, from 0.1 s (at 0.05 s it crosses the 75%
  curve on the early bump). The 50% (dashed) curve lies on the solid curve over the whole beat and
  cannot be told apart; the 75% (dotted) curve separates from them only near the peaks and merges
  elsewhere, so both are left out. The coinciding curves agree with Table 4's equal resting flows.
- LAD pressure at rest: `f5_p_rest_normal` and `f5_p_rest_50` from 0.35 s (to 0.85 s for 50%, which merges
  with Normal after about 0.88 s), `f5_p_rest_75` from 0.3 s. On the systolic rise and fall Normal and 50%
  coincide and all three converge, so the curve follower cannot keep them apart there; those times are
  left out.
- LAD flow in moderate exercise: `f5_q_ex_normal`, `f5_q_ex_50`, `f5_q_ex_75` (75% from 0.03 s).
- LAD pressure in moderate exercise: `f5_p_ex_normal`, `f5_p_ex_50` (followed from two seeds, because it
  lies under Normal from about 0.135 to 0.165 s, where its interval spans the merged ink), `f5_p_ex_75`.
- The 3D renderings above the panels carry no values. Table 4 gives the mean flows and pressures of these
  cases; a time average of a read curve cannot be formed by a run in this record.

## Fig. 6 (p. 11, journal p. 3205), 1400 dpi
Axes from the grey gridlines (y labels 0-5 cc/s, six lines found, misfit 4.4 px = 0.014 cc/s) and the
grey ticks below the x axis (0, 20, 40, 60, 80; misfit 2.0 px). Markers are found by matching their
outline (open) or body (filled) shape near the column of each x; interval: 3 px of centring plus the
calibration misfit.
- `fig6_exercise`: filled circles at 0, 40, 50, 60, 75%. Datum `Q_lad_E2_fig6`, compared with Table 4
  (`Q_lad_E2_table4`, comparison `cmp_fig6_exercise_table4`).
- `fig6_rest`: open circles at 0, 50 and 75%. The figure has no rest marker at 40% or 60% (the solid line
  passes without one; question `q_fig6_rest_points`). Datum `Q_lad_R_fig6`, compared with the Table 4
  rest flows at those three reductions (`Q_lad_R_table4_fig6pts`, `cmp_fig6_rest_table4`).
- `fig6_gould_rest` and `fig6_gould_hyperemia`: the measurements of Gould et al. (ref. 7), open and filled
  squares at 0, 40, 50, 60, 75 and 100%, recorded as measured data (`gould_rest_fig6`,
  `gould_hyperemia_fig6`). No error bars are drawn. At 100% every series ends under the exercise filled
  circle at zero flow: the hidden open square is given the circle's centre with its radius as interval,
  and the filled square, merged with the circle, the half height of the merged ink. How the canine data
  were scaled to this axis is not stated (question `q_fig6_gould_scaling`), and no model in this record
  predicts them, so they are not compared.
- The 100% point of the simulated series (zero flow, an occluded artery) is not in Table 4 and is not read.
