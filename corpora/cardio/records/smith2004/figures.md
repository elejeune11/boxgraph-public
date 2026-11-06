# Figures of smith2004

All plots in this paper are simulation output; none plots measurements. Every panel with
values is read below with code (`figures/*.py`); the shared helpers are `figures/_grid.py`
(frame, dotted gridlines, lattice calibration), `figures/_curve.py` (curve tracing) and
`figures/_loops.py` (pressure-volume loop features and curve extremes). Calibration is
always from the image. The frame and the dotted gridlines are found, their spacing gives
the step in pixels, and one labelled line (named in each file) plus the printed label
step give each line's value. A least-squares line through them gives the calibration; its
misfit is in each reading's note and is added to every interval. Each overlay in
`figwork/` (`boxgraph figure check`) was inspected; the panel overlays `figwork/panel_*.png`
and `figwork/mont*.png` show all readings of a panel together.

- **Fig. 1 (p. 3)**: circuit drawing, no values (used for the model structure).
- **Fig. 2 (p. 4)**: schematic PV diagram, no values.
- **Fig. 3 (p. 4)**: read, `fig3_driver` (from the earlier pass, unchanged). The blue
  curve e(t), calibrated on the frame and all 5 x and 9 y gridlines (misfit 0.0002 s,
  0.0011). The overlay is now inspected (`q_fig3_checked`). The curve is narrower than
  Eq. 5 with the printed B = 80: it fits B of about 100 s^-2 (`q_fig3_driver_width`).
  Compared with `driver_eq5` (`cmp_driver_fig3`).
- **Fig. 4 (p. 5)**: drawing of the heart's volumes, no values.
- **Fig. 5, top (p. 7)**: read: `fig5_vol_v010`, the solid V0 = 10 volume curve, 0.05 to
  1.75 s, traced through two beats; `fig5_vol_v080`, the dashed V0 = 80 curve on its rise
  and plateau to 0.25 s (about 96 ml), traced across the dash gaps. Calibration: x 10 lines
  0-1.8 s (misfit 0.0005 s), y 6 lines 0-100 ml (0.09 ml). The steep dashed descent
  (0.26-0.37 s) is not read: the tracer cannot bridge the dashes where the curve falls
  steeply, and the 'V0=80' arrow lies against it. No model in the record predicts Fig. 5
  (no parameters printed, `q_single_chamber`); the data are kept for later models.
- **Fig. 5, bottom (p. 7)**: read: `fig5_p2_v010`, the solid pressure P(2), 0.05 to
  1.75 s; `fig5_p2_v080`, the dashed V0 = 80 pressure at its peak only (about 130 mmHg at
  0.29-0.3 s), for the same reasons as above; `fig5_p1` and `fig5_p3`, the two constant
  boundary pressures. Those read 7.9 and 95.0 mmHg, not the 10 and 100 by eye of the
  earlier pass (`q_fig5_boundary_pressures`). Calibration: y 8 lines 0-140 mmHg (misfit
  0.06 mmHg). Where P(2) crosses P(1) or P(3) the merged run is the interval.
- **Fig. 6 (p. 7)**: read, `fig6_vspt`: the septum volume, 0.225 to 1.35 s every
  0.025 s; raster image, curve 18-24 px thick at 1200 dpi. Calibration: x 7 lines
  0.2-1.4 s (misfit 0.0004 s), y 6 lines 3.5-7 ml (exact). The swing is about 2.7 ml
  against the printed 3 ml (`q_fig6_swing`). Compared with `two_chamber_trace`
  (`cmp_fig6_vspt`).
- **Fig. 7, volumes (p. 8)**: read: `fig7_vlv`, `fig7_vrv`, each the only curve of its
  panel, 0.05 to 1.45 s every 0.05 s. Calibration: x 4 lines 0-1.5 s (misfit 0.0003 s),
  y 5 lines 40-120 ml (0.05 ml). The traces pass the 'V' and 'SV=70' labels, which do not
  touch the curves. V_lv runs 45.1-115.8 ml and V_rv 44.5-115.3 ml.
- **Fig. 7, pressures (p. 8)**: read: `fig7_pao`, `fig7_plv`, `fig7_ppu` (left);
  `fig7_ppa`, `fig7_prv`, `fig7_pvc` (right). Calibration: y 4 lines (0-150 mmHg, misfit
  0.07; 0-30 mmHg, misfit 0.02). Each curve is traced from several seeds (rank of the
  curve in a column where it is clear, one or more per beat); each column takes the
  nearest seed's trace. In ejection the ventricular and arterial curves cross. The lower
  hump is the one that continues into the slow arterial decay, so it is P_ao (P_pa), and
  the higher hump is P_lv (P_rv); the P_ao peak is about 121 mmHg. Where two curves merge
  into one run, that run's extent is the interval. P_lv and P_rv are not read where they
  run along P_pu, P_vc in late filling (about 0.75-0.9 s). All are compared with
  `closed_loop_trace` (`cmp_fig7_*`); the time origin is a choice (`q_fig7_time_origin`).
- **Fig. 8 (p. 8)**: read: left ventricle `fig8_lv_edv`, `fig8_lv_esv`, `fig8_lv_pmax`;
  right ventricle `fig8_rv_edv`, `fig8_rv_esv`, `fig8_rv_pmax`, each indexed by P_th
  (-4, 0 mmHg). Raster: grey frame and grid read with a lighter ink threshold; a 13 px disk
  opening removes the grid dots. Loop sides are the vertical runs of the loop line, peaks
  the top of each arc, traced from the top of the loop's left side. Calibration: LV x 5
  lines 50-150 ml, y 7 lines 0-140 mmHg (misfit 0.25); RV x 5 lines 40-120 ml (0.23 mmHg).
  The right-ventricle sides are searched below 12 mmHg, under the labels. Which loop is
  which follows the labelled arrows; the left sides of the LV loops follow their arcs
  (`q_fig8_stroke_volume_drop`). Fig. 8 gives a 9.3% (LV) / 9.4% (RV) drop in stroke
  volume, as printed. Compared with `closed_loop_loops` (`cmp_fig8_*`).
- **Fig. 9, left (p. 8)**: read: `fig9_lv_edv`, `fig9_lv_esv`, `fig9_lv_pmax`, indexed by
  the R_sys factor (0.5, 1, 2), the loops nested in that order (labelled). Calibration:
  x from the 100 ml gridline and the 150 ml frame only, since the 50 ml gridline lies
  under the 0.5 x loop's left side, so no x misfit can be estimated; y 6 lines 20-180 mmHg
  (misfit 0.14). Compared with `closed_loop_loops` (`cmp_fig9_*`).
- **Fig. 9, right (p. 8)**: read: `fig9_rv_edv` (right sides, 2 x, 1 x, 0.5 x left to right,
  labelled), x 5 lines 60-140 ml (misfit 0.07 ml). The left sides of the three loops lie
  on one another (about 60-62 ml) and their tops are within 1-2 mmHg of each other where
  the arcs overlap; neither is read (curves indistinguishable).
- **Fig. 10 (p. 9)**: read: `fig10_pao_max`, `fig10_pao_min`: the highest and lowest point
  of each of the three aortic pressure curves (2 x, 1 x, 0.5 x R_sys, top to bottom,
  labelled). The time axis has no ticks and is not used; y 5 lines 40-140 mmHg (misfit
  0.16). Values 164.2/130.5, 121.2/78.2 and 85.4/38.0 mmHg (`q_fig10_pressures`). Compared
  with `closed_loop_loops` (`cmp_fig10_*`). The curves as functions of time are not read:
  without time ticks they cannot be calibrated.
- **Fig. 11 (p. 9)**: read: `fig11_lv_edv`, `fig11_lv_esv`, `fig11_lv_pmax`,
  `fig11_rv_edv`, `fig11_rv_esv`, `fig11_rv_pmax`, each loop read from its own colour
  (red 2 x, blue 1 x, magenta 0.5 x E_es). Calibration: x 6-7 lines (misfit 0.16 / 0.20 ml),
  y 9-10 lines (misfit 0.22 mmHg). The blue LV right side lies under the red one; it is
  read at the blue line's rightmost pixels, with the interval covering the red line. Peaks
  are each colour's highest pixel; a black arrowhead covers the very top of the magenta
  arc, where the arc is flat. Compared with `closed_loop_loops` (`cmp_fig11_*`), scaling
  the free-wall E_es (`q_fig11_septum`).

**What the figures settle.** `q_fig3_unchecked` (the Fig. 3 overlay is checked and
correct). `q_baseline_fig7_vs_fig8_9` (confirmed with calibrated values; Fig. 11's
baseline differs again, `q_fig_baselines`). The printed 9% (Fig. 8 agrees,
`q_fig8_stroke_volume_drop`). The 120/80 -> 165/130 mmHg of the abstract (Fig. 10 agrees,
`q_fig10_pressures`). The boundary pressures of Fig. 5 (`q_fig5_boundary_pressures`).
