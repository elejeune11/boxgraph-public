# Figures of westerhof1969

The first reading digitized no figure (the figure tools were not available then). This pass reads
the plotted results with calibrated code readings (`figures.yaml`, code in `figures/`). The shared
code is `figures/_w69.py`; each figure's labels and search windows are in `figures/_fig<N>.py`.

How every reading is calibrated: the crop is rendered at 900 dpi (1200 dpi for Fig. 7) and,
for the figures printed sideways (Figs. 5, 6, 7, 10), turned upright. The scan's tilt is measured
on the longest straight line (an axis). The abscissa ticks are the stubs on the labelled frequency
axis and the ordinate ticks are the stubs beside the ordinate line. Both are matched to the printed
labels by the linear map that matches the most labels, and each axis is fitted by a straight line.
The worst tick misfit enters every interval. The misfits are at most 4.2 px in frequency and
5.5 px in ordinate, and each reading's note gives its own. The bold (model) lines are found by
stroke width: a morphological opening for Figs. 3 and 10, and for Figs. 5, 6 and 7 a best path
through the ink scored by the local stroke half-width from a distance transform, which follows the
bold line through crossings. Every magenta mark was checked on the overlay
(`figwork/<reading id>.png`; regenerate with `boxgraph figure check`).

## Read

- **Fig. 3, upper panel (p. 11)**: `fig3e_mod`, the bold curve e (NEW RADII, final model,
  R = 1420), |Z_in| at 1-11 cps. The bold line ends just short of 12 cps. Misfit 3.6 px (x), 2.5 px (y).
  Datum `fig3e_mod_fig`.
- **Fig. 3, lower panel (p. 11)**: `fig3e_phase`, curve e, phase at 1-11 cps. Misfit 3.6 / 2.2 px.
  Datum `fig3e_phase_fig`.
- **Fig. 5, upper panel (p. 13)**: `fig5_model_mod`, the bold model line for a whole leg,
  |Z_in|/R x 100 at 2-11 cps. At 1 cps the model line runs inside the near-vertical bundle of the
  subjects' lines and cannot be told apart, so it is not read there. The abscissa 0 is the corner
  label, taken on the ordinate line; without it the match slipped one tick. Misfit 4.2 / 1.3 px.
  Datum `fig5_model_mod_fig`.
- **Fig. 5, lower panel (p. 13)**: `fig5_model_phase`, bold line, phase at 1-11 cps. Misfit
  4.2 / 2.2 px. Datum `fig5_model_phase_fig`.
- **Fig. 6, upper panel (p. 16)**: `fig6_model_mod`, the solid (bold) model line, |Z_in|/R x 100
  at 2-12 cps. At 1 cps it is inside the bundle of measured lines. Misfit 4.1 / 1.7 px. Datum
  `fig6_model_mod_fig`.
- **Fig. 6, lower panel (p. 16)**: `fig6_model_phase`, model line, phase at 1-11 cps. Misfit
  4.1 / 5.5 px; the phase ticks are less even than the others. Datum `fig6_model_phase_fig`.
- **Fig. 7 (p. 16)**: three readings, all at misfit 2.8 px (x) and 0.6 px (y).
  - `fig7_model`: the thick line (final model) at the harmonic frequencies printed in Fig. 4
    (1.34 ... 9.14 cps). The model's points are vertices of the polyline, and their markers
    overlap Luchsinger's dots and bars. So each vertex is read by fitting the clean line on
    either side (0.08-0.45 cps away) and evaluating it at the vertex. The first and last vertices
    use one side only. Datum `fig7_model_fig`.
  - `fig7_luchsinger`: Luchsinger et al. (1964), dots with error bars (dashed line), at the same
    harmonics. Origin `measured`. Error bars `unstated`: neither the caption nor the text says what
    they are. Both ends are read; the bar ends are clear. At 2.63, 3.91, 6.55, 7.82 and 9.14 cps
    the dot merges with the model's thick line and marker, so the interval of the dot covers the
    merged blob. Datum `fig7_luchsinger_fig`.
  - `fig7_gabe`: Gabe et al. (1964), dots with error bars (dash-dot line), ten points near
    1, 2, ..., 10 cps, at the frequencies read from the image. Origin `measured`, error bars
    `unstated`. Datum `fig7_gabe_fig`.
  - Bars are told apart by where they stand. Gabe's points lie near whole cps and Luchsinger's at
    the harmonics of 1.31 cps. The closest pair, at 3.91 and 3.98 cps, is 17 px apart at 1200 dpi.
- **Fig. 10, left, upper panel (p. 20)**: `fig10a_mod`, case (a) normal (bold solid line,
  R = 1420), |Z_in| at 1-11 cps. Misfit 3.2 / 1.5 px. Datum `fig10a_mod_fig`.
- **Fig. 10, left, lower panel (p. 20)**: `fig10a_phase`, case (a), phase at 1-11 cps. Misfit
  3.2 / 1.4 px. Datum `fig10a_phase_fig`.

Comparisons added: Fig. 3e, Fig. 6 and Fig. 10(a) plot the same final model at R = 1420.
`cmp_fig3e_fig10a_mod`, `cmp_fig3e_fig10a_phase` and `cmp_fig3e_fig6_phase` check that its plots
agree (consistency). `cmp_fig7_model_luchsinger` sets the final model's apparent velocity against
Luchsinger's at the same harmonics (validation). The analog network itself cannot be run
(`q_network_not_runnable`), so no run reproduces these curves.

On open questions:
- `q_impedance_level_85`: `fig3e_mod` and `fig10a_mod` give the final model's |Z_in| in
  g cm^-4 s^-1, and `fig6_model_mod` gives it as |Z_in|/R x 100 with R = 1420. Their values above
  about 3 cps show the high-frequency level that p. 139 calls "about 85". That level can be set
  against the 75 computed for the proximal aorta (p. 140). No comparison is recorded because the
  two are different quantities: an input impedance level and a characteristic impedance.
- p. 139 also says the plateau of the apparent velocity (Fig. 7) is close to the local phase
  velocity 1/sqrt(L'C'). The record computes that velocity from p. 140's inputs (`c_aorta_printed`,
  "≈ 5" m/s). `fig7_model_fig` at 3.91-9.14 cps gives the model's plateau for that check. Here
  too the quantities differ (apparent vs local phase velocity), so no comparison is recorded.
- `q_figures_not_read` (first reading) is partly settled by this pass. The figures still left out
  are listed below.

## Left out

- **Fig. 1 (p. 4)**: circuit diagram of one segment. A drawing; no values.
- **Fig. 2 (p. 9)**: layout of the 121-segment network. A drawing; no values.
- **Fig. 3, curves a-d (p. 11)**: four thin lines (solid, dashed, dash-dot, dash-three-dots)
  of the earlier model versions. They cross each other a dozen times and differ only in dash
  pattern, which code cannot tell apart reliably at the crossings. Only the bold curve e is read.
- **Fig. 4 (p. 13)**: amplitude and phase delay of the pressure harmonics along the aorta. There
  are 14 small sub-panels (7 frequencies x 2 sides), each with the prototype, the intermediate
  version, the final model and Luchsinger's dashed line overlapping. The Luchsinger error bars
  are a few pixels long and many are hidden under the lines. The phase panels have no zero line
  per frequency, only the converging start point and one 100-degree scale bar. Curves
  indistinguishable. Luchsinger's apparent velocities derived from these delays are read in Fig. 7.
- **Fig. 5, Patel et al. (1965) points (p. 13)**: one thin polyline per subject. The dots are
  barely wider than the lines (a distance-transform test finds no clean separation), and below
  2 cps all subjects' lines merge into one near-vertical bundle. Individual points or subjects
  cannot be told apart reliably. A later reading by hand-assisted marker picking could add them.
- **Fig. 6, Patel 1965 (dots), Patel 1964 (open circles), Gabe 1964 (crosses) (p. 16)**: the same
  difficulty. About ten crossing polylines with small markers, merged at low frequency, and the
  open circles and crosses are smaller than the line crossings. Left out for the same reason.
- **Figs. 8, 9, 11 (pp. 15, 18, 21)**: oscillograph photographs of pressure and flow waves. They
  have no axes and no zero lines, only a per-division calibration in the caption, and the traces
  overlap. No calibrated reading is possible.
- **Fig. 10, left, cases (b), (c), (d) (p. 20)**: R = infinity (dash-dot), R = 220 (dashed) and stiff
  walls (dash-three-dots). These are thin lines differing only in dash pattern and they cross
  repeatedly. Case (d) would test the "about 50 per cent higher" impedance level (`dZin_stiff_printed`).
  A reading would have to follow the dash pattern, which was not reliable here.
- **Fig. 10, right (p. 20)**: wave travel along the aorta for the four cases. It has the same
  structure as Fig. 4 (7 frequencies, overlapping line styles, no per-frequency zero) and is left
  out for the same reason.
