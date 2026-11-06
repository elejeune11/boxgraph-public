# Figures of ursino1998

Read on 2026-11-03 with the record's own reading code (`figures/`), every panel rendered at
1500 dpi. All figures are scans, tilted by up to 0.3°: each crop is straightened first (the angle
is in every value's note). Each reading is calibrated on the panel's own axis lines and tick marks
(or dotted grid lines) matched to the printed labels; the misfit below is the largest distance, in
pixels at 1500 dpi, between a mark and the fitted axis. Shared code: `_u98.py` (ink, lines, ticks,
grid dots, straightening, curve runs), `_excel.py` (spreadsheet-style panels, marker shapes),
and one `_figN.py` per figure.

An earlier pass had read no figure (q_figures_not_read). Its eye-read notes are replaced by the
readings below; no earlier datum was eye-read from a figure, so none is kept or changed.

## Read

- **Fig. 2 top (p. 3), pressure-volume loop**: left out. It is a closed loop (two pressures at
  each volume, its four phases drawn over each other at the corners) of the same simulation as
  the middle and bottom panels, and no model in the record outputs a loop.
- **Fig. 2 middle**: `fig2_sap`, the continuous line (systemic arterial pressure) at 9 times.
  x: frame side (0) and inward ticks 0.5, 1, 1.5 s, misfit 1.9 px; y: frame bottom (0), ticks 50,
  100, frame top (150), misfit 1.7 px. The dashed left-ventricle pressure is left out: its dashes
  merge with the arterial line during ejection and lie on the frame in diastole. No model run (the
  record's models give mean values, not waveforms).
- **Fig. 2 bottom**: `fig2_co`, flow out of the left ventricle at 6 times in the two ejections
  (the flow is zero on the frame's bottom side in diastole). Misfit x 2.7 px, y 1.8 px. No run.
- **Fig. 3 top (p. 6)**: frame with inward ticks; x frame side (0) and ticks 100, 200 %, misfit
  2.0 px; y frame bottom (0) and ticks 20, 40 spikes/s, misfit 0.0 px. Elements told apart by
  shape (see `_fig3top.py`).
  `fig3top_static` (continuous line, 7 points), `fig3top_pp20` (dot-dashed, 7), `fig3top_pp40`
  (dashed, 7), `fig3top_pp60` (dotted, 8; read between neighbouring dots), `fig3top_circles`
  (Chapleau and Abboud, static: 6 circles; the circle at 175% is merged with an asterisk and left
  out), `fig3top_asterisks` (pulsatile data: 7). Runs of `afferent_pulsatile` (Eqs. 30-31 at
  periodic steady state, 100% = 92 mmHg, q_fig3_percent) reproduce the static, 20 and 40 mmHg
  lines; the 60 mmHg line differs at both ends (q_fig3_pp60). Validations against both data sets.
- **Fig. 3 middle**: `fig3_modulus`, log-log; x frame sides (0.001, 1) and dotted grid (0.01,
  0.1), misfit 2.6 px; y nine dotted grid lines (1-9) and frame top (10), misfit 0.8 px. Compared
  with `afferent_transfer` (Eq. 30 in the frequency domain).
- **Fig. 3 bottom**: `fig3_phase`; x as the middle panel; y frame bottom (0) and the dotted grid
  line (100°): two marks, so the y misfit cannot be checked. Compared with `afferent_transfer`.
- **Fig. 4 (p. 6)**: left out. Both panels are 3-D perspective surfaces (heart-rate change over
  vagal and sympathetic rates): a value cannot be located from the drawn axes without
  reconstructing the projection, and the grid nodes hide one another.
- **Fig. 5 top (p. 7)**: Starling curves at six carotid pressures. x ticks 0-10 mmHg, misfit
  1.2 px; y ticks 0-200 ml/s, 1.9 px. The curves do not cross for Pra ≥ 2 mmHg, so markers are
  assigned by their order at each Pra: `fig5top_62` (filled diamonds), `fig5top_87` (filled
  triangles), `fig5top_122` (filled circles), each 7 points (Pra 4-10; at 2-3 mmHg the filled
  markers touch); `fig5top_82` (open squares) and `fig5top_102` (open circles), 7 points each.
  The 92 mmHg series (× marks) is left out: thin crosses on crossing lines could not be found
  reliably. At Pra = 1 mmHg all six markers overlap. No run: the Starling preparation (fixed
  Pra, SAP held at 92 mmHg) is not in the record's models (q_figures_read).
- **Fig. 5 bottom**: `fig5bot_mod` (filled diamonds; 3 of 6 points, the others overlap open
  circles) and `fig5bot_exp` (Kostiuk et al., open circles, 6 points). No run (as above).
- **Fig. 6 top**: `fig6_co`, 17 filled diamonds (40-200 beats/min), misfit x 0.2, y 1.6 px.
  Compared with `pacing_curve` (heart period imposed, other reflexes closed loop).
- **Fig. 6 middle**: `fig6_sv`, 18 filled diamonds (30-200 beats/min), misfit 1.5 / 1.3 px.
  Compared with `pacing_curve`.
- **Fig. 6 bottom**: x axis on top (70 at the y axis, ticks 110-190), y ticks -1 to 0 (0 on the
  x axis line), misfit 1.9 / 1.6 px. `fig6_dsv_mod` (10 diamonds, 100-190 beats/min; the 80 and
  90 points are covered by open circles) and `fig6_dsv_exp` (Melbin et al., 12 open circles). No
  model run: the record has no derivative of stroke volume over heart rate.
- **Fig. 7 (p. 8)**: six panels, x ticks 0-2 (norm.) with 0 at the y axis, misfit ≤ 3.8 px,
  y misfit ≤ 3.9 px. Model lines are the ink surviving a 16-px opening, in long pieces;
  markers are blobs of ~115 px after a 44-px opening.
  - top left: `fig7a_model` (7 points, x 0.45-1.4; at 1.6 the line runs on the frame among the
    Brunner markers and is not read) and `fig7a_brunner` (the three diamonds at 0.4: mean and
    ± SD; the group at 1.6 is hidden under the lines). Compared with `static_volume_shift`
    (q_fig7_volume_shift, q_fig7_axes).
  - top right: `fig7b_model`, `fig7b_brunner`, as top left.
  - middle left: `fig7c_model` (8 points) and `fig7c_eckberg` (Eckberg and Sleight, 7 squares,
    two pairs split where they overlap). Read in mmHg (q_fig7c_axis); compared with
    `static_period_change`.
  - middle right: `fig7d_model` (8 points), `fig7d_cox` (8 filled circles), `fig7d_shoukas` (2 of
    3 open squares). Compared with `open_loop_static` (validations run vagotomized). Angell-James
    (+) and Potts (*) are left out: thin crosses on the dashed lines could not be detected
    reliably.
  - bottom left: `fig7e_intact` (4 points, x ≤ 0.9; beyond, the intact, vagotomized and data lines
    merge) and `fig7e_schmidt` (filled triangles). The vagotomized model line is left out: in this
    scan Potts' connecting line is as thick as it, and the two could not be told apart; Chen (×)
    and Potts (*) are left out as above.
  - bottom right: `fig7f_intact` (4 points), `fig7f_schmidt` (5 triangles); vagotomized line and
    Potts left out as above.
- **Fig. 8A (p. 9)**: x ticks 20-160, misfit 2.4 px; y 0-200, 3.7 px. `fig8a_20` (filled squares,
  5), `fig8a_30` (open triangles, 8), `fig8a_40` (filled circles, 6): squares and circles told
  apart by ink in the corners of the marker's box; markers overlapping others are left out. The
  0-mmHg series (×-asterisk marks) is left out (thin crosses). No run: the record's circulation
  model holds the carotid pressure only constant, not pulsating.
- **Fig. 8B**: Schmidt et al.'s data, `fig8b_25` (3), `fig8b_50` (2), `fig8b_75` (3), same
  method; 0 mmHg left out as above. No model predicts them (the amplitudes differ from Fig. 8A's).
- **Fig. 9 top**: bars, y ticks -20 to 30 (0 where the zero line crosses), misfit 2.8 px.
  `fig9top_model` (grey) and `fig9top_exp` (Kumada et al., white), one bar per variable
  (x = 1 SAP, 2 CO, 3 HR, 4 R), the value at the bar's end. Compared with each other (validation
  of the paper's own plotted prediction).
- **Fig. 9 bottom**: `fig9bot_basal`, `fig9bot_nores`, `fig9bot_nounstr`, `fig9bot_noemax`,
  `fig9bot_nohr`, 4 bars each (bars of about zero height read on the zero line, with that
  interval). The basal bars are compared with the top panel's model bars (consistency). No
  hemorrhage model in the record (q_figures_read).

## What the figures settle

- q_figures_not_read: answered for Figs. 2, 3, 5-9 (Fig. 4 left out, above).
- q_pacing_start: Fig. 6 top shows the paper's own pacing curve; both candidate starting rates give
  about the stated 15% (see q_figures_read), so the figure does not decide between them.
- The x axis of Fig. 3 top is consistent with 100% = 92 mmHg (q_fig3_percent); that of Fig. 7
  middle left is in mmHg, not normalized (q_fig7c_axis).
