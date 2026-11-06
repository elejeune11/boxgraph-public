# Figures of boileau2015

All figures are vector graphics (matplotlib), so every reading renders its panel at 1200 dpi and
reads it with code. Calibration is from the image: the plot frame and the dotted grid lines are found
and matched in order to the printed tick labels; a straight-line fit gives the scale. The misfit is
under 1 px on every axis, and intervals carry a 0.5 px floor. Shared code: `figures/_fig2.py` (Fig. 2)
and `figures/_wave.py` (the red curves of Figs. 3-9). Each panel's file names only its tick labels,
whether the frame lines carry the end labels, and (for the first panel of a figure) the legend box to
ignore. Every reading was checked with `boxgraph figure check`, and the overlays were inspected.

An earlier pass read no figure (its tools were refused). Its eye-read data are kept unchanged; none of
them was a figure reading.

## Read

- **Fig. 2(a)-(f)** (p. 8), single pulse, one panel per scheme (DCG, LCG, FEM, FVM, McC, STM).
  - `fig2{a..f}_eq15`: the thick black line (Eq. 15), at 14 positions x = 0.7-9.9 m chosen between the
    pulses. In each column it is the only ink run 8-30 px tall. Frame (y = 0, 1; x = 0, 10) plus dotted
    grid (0.2-0.8; 2-8; the x = 4 line is hidden behind a pulse in some panels and is not used). Misfit
    0.5-0.75 px; intervals about +-0.004 (the line's half-thickness). Data `fig2{a..f}_eq15_curve`;
    runs `run_eq15_fig2{a..f}` sweep model `peak_decay_eq15` over these x; comparisons
    `cmp_eq15_fig2{a..f}` (reproduction). This settles the reading owed by `q_fig2_unread`
    (see `q_fig2_read`).
  - `fig2{a..f}_tips`: the tips of the eight inviscid pulses (thin solid lines), one point per pulse,
    indexed by the pulse's position. Most tips reach the top frame and are reported as hidden by it
    (y in [0.995, 1.002]). The few below it (LCG at 1.1-1.5 s: 0.994, 0.993, 0.991; FEM at 1.5 s: 0.994;
    FVM at 0.1 s: 0.994) are read to +-0.0015. Data `fig2{a..f}_tips_points` (solver output, no model
    here). They bear on the text's 'less than 0.9%' inviscid peak loss (`q_fig2_read`).
  - Left out: the dashed viscous pulses. Their tips lie inside the thin inviscid pulse lines and under
    the thick Eq. 15 line, so they cannot be told apart in any column.
- **Fig. 3(a)-(d)** (p. 10), common carotid: the red '3D' line (the 3D model of [33]) in each panel.
  Readings `fig3a_P_3d` (51 points), `fig3b_dP_3d` (52), `fig3c_Q_3d` (41) and `fig3d_dr_3d` (51), at
  t = 0.01-1.09 s every 0.02 s where the red line shows. Data `fig3*_3d_curve` (predicted, from [33]).
- **Fig. 4(a)-(d)** (p. 12), upper thoracic aorta: the red '3D' line. `fig4a_P_3d` (45), `fig4b_dP_3d`
  (40), `fig4c_Q_3d` (45), `fig4d_dr_3d` (45), at t = 0.01-0.93 s.
- **Fig. 5(a)-(c)** (p. 17), aortic bifurcation, three rows (aorta midpoint, aorta end point, iliac
  midpoint): the red '3D' line in all nine panels. `fig5{a,b,c}_{mid,end,iliac}_{P,Q,dr}_3d`
  (28-55 points each), t = 0.01-1.09 s. In the Δr panels of the top two rows the frame carries no
  label; there the grid lines alone calibrate the y axis.
- **Figs. 6-9** (pp. 18-21), 37-artery network: the red 'Exp.' line, the in vitro measurement of [45]
  (origin measured), in all sixteen panels (pressure left, flow right):
  Fig. 6(a) aortic arch II (`fig6a_P_exp` 38 points, `fig6a_Q_exp` 40), 6(b) thoracic aorta II (38, 38);
  Fig. 7(a) left subclavian I (39, 40), 7(b) right iliac-femoral II (40, 41);
  Fig. 8(a) left ulnar (40, 40), 8(b) right anterior tibial (36, 41);
  Fig. 9(a) right ulnar (35, 38), 9(b) splenic (36, 37), at t = 0.01-0.81 s every 0.02 s.
  Data `fig{6..9}{a,b}_{P,Q}_exp_curve`. No model in this record predicts them; the six solvers'
  outputs are in the supporting datasets (record `boileau_data`), where they can be validated against
  these readings.

How the red curves are read (`_wave.py`): the red line is pure red (R > 200, G and B < 90). It is drawn
first, so the 1D curves cover it wherever they coincide with it. The `at` positions of each reading are
those of the regular grid (every 0.02 s) where the red line is visible in the column. Where it is
wholly hidden, the 3D or measured value is within a line width of the 1D bundle, and no value is
recorded there. A partly covered line gives a run shorter than the line width, and the interval widens
by the hidden part. A steep stretch gives a tall run, and the interval is half its excess height. A
red line split by a curve drawn across it is merged when the gap is covered by other ink. Intervals are
a few hundredths of a kPa, a few tenths of ml/s (more on steep stretches), and about 0.005 mm.

## Left out

- **Fig. 1** (p. 5): circuit diagram of the three-element Windkessel. No values.
- **Fig. 10** (p. 22): topology of the ADAN56 network. No values.
- **The six 1D scheme curves of Figs. 3-9**: they overlap within line width almost everywhere
  ('no significant differences between the six schemes'), so no single scheme can be told apart. Where
  they separate (e.g. LCG in Fig. 9(b)), it is over short stretches. Their outputs are released in the
  supporting datasets.
- **Figs. 11-14** (pp. 25-28), ADAN56 pressure and flow waveforms, and **Figs. 15-16** (pp. 29-30),
  ADAN56 pressure along the aorta: six-scheme solver outputs only, with no measurement and no reference
  solution. DCG, LCG, FEM, FVM and McC overlap within line width ('differences cannot be appreciated in
  the scale of the figures'). STM (yellow) separates in places and could be read later. No model of
  this record predicts any of these curves, and the waveforms are in the supporting datasets
  (record `boileau_data`).
