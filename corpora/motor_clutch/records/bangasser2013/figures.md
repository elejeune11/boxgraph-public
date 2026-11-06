# Figures of bangasser2013

## Second pass (2026-10-31): calibrated readings

This pass could run the figure tools. Every figure that plots values now has calibrated readings
by the record's own code (98 readings in `figures.yaml`, 100 stubs in `figures/`). Each stub names
one series and the printed axis labels, then calls the shared code in `figures/_panel.py`, pinned
by its SHA-256. The stubs `fig3a_nc_x3.py` and `fig3a_nm_x3.py` are left over: they were written
for two curves later found hidden, and no reading uses them.

**Method (all from the image).** The axis spines are the longest dark lines. The tick marks are
the short dark strokes outside them, matched in order to the printed labels (linear or log10 fit).
The misfit is the largest residual, and never under 0.5 px. Where a coloured line covers the x
axis (Figs. 2C, 3A, 1B), the axis is put at the y axis's 0 tick and the x ticks are found below it.
Series are found by colour, using the nearest of the panel's series colours within a tolerance.
- **Curves:** the run of the colour in each pixel column, followed by continuity. The value is the
  run's centre. The 95% interval is half the line thickness, plus half the run's excess over that
  thickness where the line is steep, plus the y misfit, plus 1 px, plus the slope times the x misfit.
- **Markers:** cores of the distance map; each marker is a disc much thicker than any line.
- **Error bars:** the thin dark line through a marker's column. The cap's middle row is the bar's
  end. A bar hidden inside its marker is reported as at most the marker.
- **Bars:** the top edge of each coloured bar standing on the axis, matched in order to the
  printed category labels.

Every reading was run with `boxgraph figure check` (overlays in `figwork/`). I looked at the
overlays, and at larger-marker versions (`figwork/rev_*.png`) for the marker panels: the marks sit
on the intended series.

The readings also agree with each other. The base-set flow curve is plotted seven times (Figs. 2C,
3A ×8 green, 4A, 4C, 6B, 6D, 6E). At 0.01, 0.1, 1 and 100 pN/nm every copy reads 84.9-85.3,
73.6-73.9, 100.3-100.6 and 108.7-109.0 nm/s (where the curve is read there). The exception is the
vu panel of Fig. 3A, whose axis runs to 1500 nm/s: it reads 85, 72, 97 and 105 nm/s, within its
±17 nm/s intervals. The base traction of Fig. 2B and Fig. 6E agrees to
0.1 pN.

| Panel | Readings (datum) | What | Calibration (x / y misfit, px) |
|---|---|---|---|
| Fig. 1A (p. 2) | `fig1a_u87`, `fig1a_smc`, `fig1a_neut`, `fig1a_nih3t3` (`migration_fig1a_*`, measured) | the points of the four cell types with error bars (refs. 4, 11, 10, 2); 3+5+3+2 points | 4 decade ticks, 8 y ticks; 0.8 / 2.0 |
| Fig. 1B (p. 2) | `fig1b_neuron`, `fig1b_t24`, `fig1b_baec` (`traction_fig1b_*`, measured) | the points with error bars (refs. 15, 7, 12); 2+3+3 points | 3 ticks (0.1, 10, 1000), 8 y ticks; 0.7 / 0.9 |
| Fig. 2B (p. 4) | `fig2b_nc50`, `_nc100`, `_nc5`, `_nc300` (`F_fig2b_*_read`) | traction, the four nc curves | 5 / 6 ticks; 1.6 / 0.5 |
| Fig. 2C (p. 4) | `fig2c_nc50`, `_nc100`, `_nc5`, `_nc300` (`v_fig2c_*_read`); `fig2c_optima` (`ksopt_fig2c_read`) | flow, the four nc curves; the x positions of the two dashed optimum lines (nc = 50: 0.137, nc = 100: 0.405 pN/nm) | 5 / 7 ticks; 2.0 / 1.4 |
| Fig. 3A (p. 5) | `fig3a_<p>_<x01,x03,x1,x3,x10>` (`v_fig3a_*`), 38 readings | flow for each parameter at 0.1-10 times its base value; parts lying under another curve are not read (q_fig3a_hidden_curves) | 3 / 3 ticks each (vu: 4 y ticks); 0.5-2.0 / 0.5-2.0 |
| Fig. 4A-D (p. 5) | `fig4a_s1..s6`, `fig4b_s1..s6`, `fig4c_s1..s4`, `fig4d_s1..s4` | flow and traction under coordinate changes; only the end curves have printed parameters (q_fig4_intermediate_series) | 4 decade ticks; A 2.8/0.9, B 2.8/1.1, C 1.6/1.3, D 3.8/0.9 |
| Fig. 6B (p. 7) | `fig6b_kens` (`kens_fig6b_read`), `fig6b_flow` | ensemble clutch stiffness (right log axis, labelled nm/s: q_fig6b_axis_unit); grey flow | 5 / 7 left, 5 right ticks; 2.0 / 2.0 |
| Fig. 6D (p. 7) | `fig6d_cycle` (`tcycle_fig6d_read`), `fig6d_binding` (`tbinding_fig6d_read`), `fig6d_flow` | cycle time (right axis), the dashed binding-time line (6.4 s), grey flow | 5 / 7 left, 8 right ticks; 4.5 / 2.1 |
| Fig. 6E (p. 7) | `fig6e_flow`, `fig6e_traction` | the base-set flow (left) and traction (right) over the shaded regimes | 5 / 7 left, 10 right ticks; 2.0 / 1.6 |
| Fig. 7A (p. 8) | `fig7a_blue`, `fig7a_minus_clutch`, `fig7a_minus_motor` (`F_fig7a*_read`) | the six bar heights (1350, 819, 473, 415; 116; 591 pN) | 9 y ticks; – / 1.8 |
| Fig. 7B (p. 8) | `fig7b_blue`, `fig7b_red` (`hist_fig7b_*`) | clutch-length histograms bar by bar (14 and 9 bars) | 4 and 5 y ticks; – / 0.75, 2.5 |
| Fig. 7C left (p. 8) | `fig7c_kong` (`tau_kong_fig7c`, measured, ref. 32); `fig7c_fit` (`tau_fig7c_read`) | Kong et al.'s 12 lifetimes with error bars; the fitted catch-slip curve | 8 / 9 ticks; 1.2 / 1.2 |
| Fig. 7C right (p. 8) | `fig7c_right_s1..s6` | flow of the catch-slip motor-clutch model, six nm = nc (q_fig7c_right_model) | 4 / 9 ticks; 1.7 / 1.5 |
| Fig. S1A (p. 20) | `figS1a_present` (`v_figS1a_present_read`), `figS1a_chan` | the new algorithm and Chan and Odde's original output on the same parameters | 4 / 7 ticks; 1.7 / 0.8 |
| Fig. S1B (p. 20) | `figS1b_points` (`v_figS1b_measured`, measured, ref. 15), `figS1b_present` | Chan and Odde's 6 neuron flow rates with error bars; the base-set curve against modulus | 4 / 7 ticks; 2.6 / 0.5 |

**Runs and comparisons.** Each predicted curve whose parameters are printed has a run of the
record's model at the read x positions, and a comparison:
- motor_clutch_ssa: Figs. 2, 3A, 4 (end curves), 6, 7A, S1A;
- optimal_stiffness, swept over nc: the Fig. 2C optima;
- Eq. 10: the Fig. 6D binding time;
- Eq. 9: the fitted curve of Fig. 7C (reproduction) and Kong et al.'s points (fit_quality).

The Fig. 3A multipliers are applied through new Eq. 5 models (`scale_<p>_eq5`). Fig. 6 is taken
to use the base set, as before. No run is possible for:
- Fig. 1 and Fig. S1B points: no model of this record predicts them, and the modulus-to-spring-
  constant conversion is not given;
- Fig. 7B: no model outputs a length histogram;
- Fig. 7C right: catch-slip motor-clutch, not built;
- the intermediate Fig. 4 curves;
- Fig. S1A's 2008 curve: the old algorithm.

**Verdicts (computed from the cached build, 2026-10-31).** Of the 68 comparisons against these
readings, 45 reproduce, 10 are close and 13 do not. The 13 are explained in
q_second_pass_differences:
- stalled curves at the softest stiffness (the loading transient of q_stall_transient);
- one point on a near-vertical jump;
- Fig. 4C-D kon = 3, koff = 1 /s at high stiffness, off by 3-4 nm/s;
- the Fig. 7C fitted curve, which peaks 8% below Eq. 9 with the printed parameters;
- Kong et al.'s low-force points, which Eq. 9 does not fit;
- the binding time.

**Open questions the figures settle or sharpen.**
- *q_tbinding:* the calibrated line is at 6.4 s, against 15.0 s from Eq. 10 (q_tbinding_calibrated).
- *q_measured_points_not_read:* those points are now read (q_measured_points_read).
- *q_eye_readings:* every eye-read datum now has a calibrated twin, which carries the verdict. The
  eye-read data are kept unchanged.

## Left out, and why

- Fig. 1A-B Gaussian curves (solid and dashed): fits drawn "to show potential stiffness optima",
  with no parameters given; the measured points themselves are read.
- Fig. 2A, Fig. 3B legend box, Fig. 6E shading and arrows, Movie S1: drawings or schematics.
- Fig. 3A, nc × 3 and nm × 3 curves: hidden over the whole panel under the 10-times curve.
- Fig. 3B, Fig. 5A-C, Fig. S1C, Table S1: tables of printed numbers, recorded from the page images
  in the first pass (q_tables_from_image).
- Fig. 5D: a 3D surface in perspective. Its axes cannot be calibrated from a 2D projection, so no
  value can be read with an honest interval.
- Fig. 6A, Fig. 6C, Fig. 7A traces (right of the bars), Fig. 7B time traces: single random
  trajectories of the simulation.
- Fig. 6B dashed substrate line and circle; Fig. 6D circle: the identity line κ = κsub and markers
  of a crossing. They are drawn constructions, not results.

## First pass (kept for the record)

In the first reading, and in the audit, the figure tools could not be run. Plotted values were
read by eye from the 110 dpi page images and recorded with `≈` (no verdict). They stay unchanged:

- Fig. 2B-C: `v_fig2c_nc*`, `F_fig2b_nc*`, `ksopt_fig2_base`
- Fig. 6B: `kens_fig6b`
- Fig. 6D: `tcycle_fig6d`, `tbinding_fig6d`
- Fig. 7A: `F_fig7a*`
- Fig. 7C: `tau_fig7c`
- Fig. S1A: `v_figS1a_present`

Their calibrated counterparts are listed above.
