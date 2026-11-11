# Figures of wan2002

Every plotted curve of Figs. 1-5 is read by code (`figures/<reading id>.py`, all built on the shared
`figures/_wan.py`; its docstring gives the method). In short: the page is rendered at 1100 dpi
(Fig. 1), 1500 dpi (Fig. 2), 2000 dpi (Figs. 3, 4) or 1200 dpi (Fig. 5). Each axis is calibrated
from its own tick marks, matched in order to the printed tick labels and fitted by a straight line;
the worst misfit is in each reading's note and is added to every interval. The solid curve is the
cheapest unbroken path through the ink, and the dashed curve is the ink off that path. Each value
is the centre of the stroke in the column of x, and its interval is the stroke's extent there
(wide where the curve is steep or the two curves touch), widened by the misfits. Every reading
was checked with `boxgraph figure check`: the magenta crosses sit on the intended curve.

Times read: 0.05-0.85 s in steps of 0.05 s (Figs. 1-4: the curves start at 0 and end near 0.9 s,
where the two curves often meet); 0.02-0.44 s in steps of 0.02 s (Fig. 5). All data are
`<reading id>_read` in data.yaml, origin `predicted` (the paper's 1D results, and in Fig. 5 its
3D results). The paper prints no measurements: every plot is a computed result.

The paper's figures are drawings plus plots. The drawings (the tube of Fig. 1, the bifurcation
of Fig. 2, the aorta of Fig. 3, the aorto-iliac reconstruction of Fig. 4, the bypass of Fig. 5)
have no values and are not read.

## Fig. 1 (p. 6): single segment

- **Volume Flow** panel: `fig1_flow_inlet` (solid line, inlet, as the legend says) and
  `fig1_flow_outlet` (dashed, outlet). Calibrated on the 6 x ticks and 8 y ticks; misfit 1.6 px in
  x and 3.4 px in y.
- **Pressure** panel: `fig1_pres_inlet` (solid) and `fig1_pres_outlet` (dashed). Calibrated on
  6 x and 9 y ticks; misfit 2.2 px in x and 3.3 px in y. Where the curves cross (near 0.3 and
  0.7 s) the dashed value lies inside both strokes, and its interval spans them.
- Run: `run_fig1_curves` (the released solver, as `run_segment`, at the reading times).
  Comparisons: `cmp_fig1_Q_in`, `cmp_fig1_Q_out`, `cmp_fig1_p_in`, `cmp_fig1_p_out`.
- What the readings settle (`q_fig1_curves`, `q_fig_outlet_resistance`):
  - The run's inlet flow, from the release's inflow table, follows the reading of Fig. 1's inlet
    flow closely. That supports the choice of `q_inflow_waveform`.
  - The run's outlet peaks come much earlier than the figure's, which is what `q_fig1_delay`
    describes by eye. It is now a comparison.
  - Over the cycle, Fig. 1's outlet pressure follows its outlet flow at a nearly constant ratio,
    as Eq. 8 requires, close to the added `R_segment_added`.

## Fig. 2 (p. 7): symmetric bifurcation

- **A - Inlet**: `fig2a_flow` (solid, flow, left axis 20-90) and `fig2a_pres` (dashed, pressure,
  right axis 40-160). Calibrated on 6 x, 8 left and 7 right ticks; misfits up to 2.1 px in x and
  3.4 px in y.
- **B - Right Iliac**: `fig2b_flow` (left axis 10-45) and `fig2b_pres` (right axis 40-160).
- **C - Left Iliac**: `fig2c_flow` only.
  - Its right axis labels are printed too small and blurred to be read. Their tick marks are
    there, but which values they stand for cannot be taken from this panel, so the left iliac
    pressure is left out. The caption says it is identical to B's.
- In all three panels the dashed pressure runs along the solid flow line for most of the cycle.
  It stands apart only near the peaks. Where it is hidden in the solid stroke, its value is that
  stroke widened by one line thickness (`hidden_ok`, noted in each value's note), so those
  intervals are wider.
- Run: `run_fig2_curves`. Comparisons: `cmp_fig2_Q_in`, `cmp_fig2_p_in`, `cmp_fig2_Q_r`,
  `cmp_fig2_p_r`, `cmp_fig2_Q_l`.
- Consistency: `cmp_fig2_symmetry_flow` compares the left and right iliac flows (the caption's
  claim that they are identical).
- What the readings show (`q_fig2_damping`, `q_fig_outlet_resistance`):
  - Each branch's flow is about half the inlet flow, in phase with it, and its pressure follows
    its flow at a nearly constant ratio.
  - The run with the added radii and resistances damps the branch flows strongly. The figure's
    bifurcation does not.

## Fig. 3 (p. 8): idealized abdominal aorta

- Panels A (Aorta), B (Celiac), C (Superior Mesenteric), D (Left Renal), E (Right Renal),
  F (Left Iliac) and G (Right Iliac): `fig3<panel>_flow` (solid, left axis) and `fig3<panel>_pres`
  (dashed, right axis 60-120 mmHg).
- Calibration:
  - Panel A's flow axis runs 20-90. Panels B-G run 4-14 cc/s, with a tick at every integer.
  - The first time label (0.0) sits under the left axis line and the lowest flow label (4) at the
    bottom corner; they have no ticks of their own, and the axis lines stand in for them.
  - On several axes the blurred scan merges ticks with their labels. There the ticks are the
    peaks of the darkness beside the axis line.
  - Misfits are 1.8-7.1 px in x and 0.4-9.6 px in y, largest in panel D. In each panel's units
    they stay below the stroke width or near it, and they are in every interval.
- Not compared: no model in the record can produce these curves. The geometry, resistances and
  inflow are not printed (`q_examples_not_runnable`).
- The text says pressure and flow are in phase at every exit. The readings show it: each outlet's
  pressure and flow peak at the same time.

## Fig. 4 (p. 9): aorto-femoral bypass, proximal end-to-end anastomosis

- Panels A (Inlet), B (Graft), C (Graft Right), D (Graft Left), E (Right Iliac), F (Left Iliac),
  G (Right Femoral), H (Left Femoral), I (Right Popliteal) and J (Left Popliteal):
  `fig4<panel>_flow` (solid, left axis) and `fig4<panel>_pres` (dashed, right axis 85-120 mmHg).
- Calibration:
  - Flow axes: A 30-100, B 0-70, C and D 0-35, E-G 0-16, H-J 0-10 cc/s. Every panel's pressure
    axis is 85-120 mmHg.
  - All x and right-axis ticks are tick marks, except panel F's x axis, which uses darkness peaks
    and the corner.
  - Misfits are 0.4-9.1 px in x and 2.2-11.5 px in y (largest in panels I and J). At 2000 dpi
    that is under 0.25 cc/s and 0.6 mmHg, and it is in every interval.
- The solid lines of these panels have small breaks in the scan, and the dashes are long. The
  solid path skips the breaks and fills them along the line between their ends, and the slope cost
  keeps it off the dashes where the curves cross. Every overlay was checked for this.
- Where flow and pressure lines touch (A, B, I, J near their crossings), the interval spans both
  strokes.
- Not compared with a run: the plan cannot be rebuilt (`q_examples_not_runnable`).
- Table I's "AFB with end to end anastomosis" rows are this plan's mean flows. A cycle mean of a
  read curve cannot be formed by a run here, because model inputs are scalars, so they are not
  compared; `q_fig4_table1` records what the readings show by inspection.
  - The popliteal flows (I, J) stay below 5 cc/s all cycle, below the table's 5.05 and 5.72 cc/s.
  - The inlet and femoral curves are about as large on average as the table's values.

## Fig. 5 (p. 10): porcine bypass

- Panels A (Inlet Flow), B (Native Aorta Flow), C (Bypass Flow) and D (Outlet Flow):
  `fig5<panel>_3d` (solid, 3D FEM, as the legend says) and `fig5<panel>_1d` (dashed, 1D FEM).
- Calibration: 5 x ticks (0.0-0.4 s) and 8 y ticks (0-140 cc/s), all tick marks.
  Misfits are 1.6-2.7 px in x and 2.6-4.1 px in y.
- The two curves coincide over parts of each panel (by the readings, about 0-0.08 s, 0.16-0.18 s
  and 0.42-0.44 s). There the 1D (dashed) value is the 3D stroke widened by a line thickness.
  Those positions agree in the comparison by construction, which the notes of the values say.
- Comparisons: `cmp_fig5a_1d3d` to `cmp_fig5d_1d3d` (validation, 1D against 3D, as for Table I).
- The text's "peak differences ... on the order of 50% in the native aorta, but less than 10% in
  the bypass graft" (p. 8) can be read from `fig5b_*` and `fig5c_*`. No model in the record forms
  a peak or a relative difference of two curves, so these are not compared.
