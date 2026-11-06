# Figures of olufsen2000

All readings are code readings (`mode: code`) in `figures/`. Overlays from `boxgraph figure check` were
looked at for every reading: each magenta cross sits on the curve named.

## Read

First pass (unchanged): shared calibration and solid-line tracing in `figures/_common.py`, crops at 800 dpi.
Calibration fits the matched tick labels to the inward ticks found at the frame; the worst misfit is added
to every interval.

- **Fig. 3** (p. 7), `fig3_inflow`: measured ascending-aortic inflow (the model's inflow boundary condition), 3.325-4.275 s.
- **Fig. 6** (p. 12), `fig6_mean_pressure`: simulated mean pressure along the aorta, 1-41 cm.
- **Fig. 8** (p. 14), `fig8_B`, `fig8_F`, `fig8_G`, `fig8_C`, `fig8_D`, `fig8_E`, `fig8_J`, `fig8_H`, `fig8_I`:
  simulated pressure at the nine flow-measurement sites, 3.3-4.25 s. `fig8_E` (left subclavian) is the
  calibrated curve behind `q_cuff_pressure_claim`, which was read by eye.
- **Fig. B5** (p. 18), `figB5_convergence`: simulated aortic pressure 8 cm from the valve over the first 8 s.

Second pass (this pass): `figures/_fig7.py`, crops at 1000 dpi (plot box about 1800 x 1400 px).

- **Fig. 7** (p. 13), measured (dashed, 'meas') and simulated (solid, 'sim') flow at the nine sites. These
  are the paper's validation data, now readable by other records' models:
  - Aortic Arc (B): `fig7_B_meas` (12 points), `fig7_B_sim` (26). Misfit x 1.5 px, y 4.9 px.
  - Aortic Des (F): `fig7_F_meas` (13), `fig7_F_sim` (27). Misfit x 1.2, y 3.8 px.
  - Aorta Bif (G): `fig7_G_meas` (10), `fig7_G_sim` (25). Misfit x 0.4, y 5.0 px.
  - Anonyma (C): `fig7_C_meas` (18), `fig7_C_sim` (26). Misfit x 1.1, y 1.5 px.
  - L Carotid (D): `fig7_D_meas` (19), `fig7_D_sim` (22). Misfit x 1.8, y 3.3 px.
  - L Subclavian (E): `fig7_E_meas` (19), `fig7_E_sim` (26). Misfit x 1.3, y 5.0 px.
  - Brachialis (J): `fig7_J_meas` (19), `fig7_J_sim` (28). Misfit x 1.5, y 3.9 px.
  - Iliac (H): `fig7_H_meas` (13), `fig7_H_sim` (25). Misfit x 1.0, y 2.7 px.
  - Femoral (I): `fig7_I_meas` (9), `fig7_I_sim` (27). Misfit x 0.5, y 3.2 px.

  How the two black curves are separated: the solid line is the dark runs that can be followed column by
  column for about 6 line widths (a dash is 2-3 widths long, so it cannot); the dashes are what is left
  once the solid line is removed, kept as connected components of dash size (grid dots and '+' marks are
  smaller). A measured value is the centre of the dash in the reading column, or, in a gap between two
  dashes, the interpolation between their facing ends; steep stretches where consecutive dashes stack
  in one column give one tall interval. The previous pass left Fig. 7 out because the curves overlap; the
  answer here is to read only where they can be told apart. Where the dashed curve runs under the solid
  line (much of the aortic upstroke and the late diastolic tails), or where several solid runs share a
  column, no value is read and that position is left out of `at` (the `at` lists are per reading, from
  the x positions 3.3-4.25 s every 0.025 s, off the grid lines). Where a dash touches the solid line the
  solid run includes it and the 'sim' interval is wider there. The measurement is plotted without error
  bars, and the paper states no measurement uncertainty.

- **Fig. 5** (p. 12), `fig5_40cm`: the solid '40 cm' line only (simulated aortic pressure 40 cm from the valve),
  `figures/fig5_40cm.py`, same solid-line reader. In this panel the legend's lower edge lies on the 110 mmHg
  grid line and `_common.frame` took it for the top frame; the reading uses its own copy of the calibration
  with the outermost frame lines instead (misfit x 0.8 px, y 1.7 px, ticks 3.4-4.4 s and 90-120 mmHg, bottom
  frame 80 mmHg). Read where the 40 cm line runs alone (upstroke 3.41-3.49 s, peak 3.62-3.74 s, dip
  3.84-3.95 s) and, after about 3.95 s, where all four lines run together as one bundle (said in the datum's note).
  Positions where the overlay showed the run taking in the converging 10-30 cm lines were removed.

No model in the record can produce these curves: the coupled network model (`network_1d`) is not runnable
(`q_network_not_runnable`), so the new data have no runs or comparisons, and the 'never compared' warnings
for the predicted curves are expected. The measured Fig. 7 flows are recorded for validation by any later
record whose model predicts flow at these sites.

None of the record's open questions is settled by these figures: the plotted measured cycles (Figs. 3, 7)
span about 3.3-4.25 s and do not show where a beat begins or ends, so they neither confirm nor refute the
1.1 s period against 51 beats per minute (`q_period_heart_rate`).

## Left out

- **Fig. 5**, the 10, 20 and 30 cm lines (dashed, dotted, dash-dotted): broken line styles that touch each
  other over most of the cycle and cannot be told apart by dash shape reliably at this scan quality.
- **Fig. 4** (p. 11), 3D pressure surfaces p(x, t): a perspective plot, no values readable.
- **Figs. 1, 2, B1-B4**: drawings and schemes, no values.
