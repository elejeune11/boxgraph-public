# Figures of stergiopulos1992

Second figure pass (2026-11-03). Every reading is done by the record's own code (`mode: code`), from a
900 dpi render of one panel. The shared helpers are in `figures/_figlib.py`. They find the plot frame as
long unbroken lines and the tick labels as connected digit components outside the frame. Each label is
matched to its printed value and placed at the tick mark found next to it, or, where a figure prints its
end labels at the frame corners, at the frame line. A straight line is fitted through these marks; its
largest misfit in pixels is in every reading's note. The small rotation or shear of the scan (0.0-0.3°) is
measured on the frame lines and taken out. A reading's 95% interval is half the line width (widened where
the line slopes), plus the calibration misfits and the local spread of the trace. A band reading's
interval is the band itself. Overlays are in `figwork/<reading id>.png` (not committed). In each overlay the
magenta marks were checked to sit on the intended line.

Each line is recorded whole as data (`fig*_curve`). The comparisons use one stenosis level per line,
read by the same code (`fig*_at` readings → `fig*_pt` data), because a whole-curve sweep of the
autoregulated tree, repeated for every alternative of the added inputs and every rounding end, would take
hours to build (`q_figure_sweeps`). Values below are the record's model at the paper's own inputs, and
the build gives the verdicts.

Earlier pass: figures.md said no figure was digitised; its eye-read values (the added inputs T, Ts and
Qmax from Fig. 2(b)) are kept unchanged.

- **Fig. 1** (p. 3): left out. A drawing of the 55-segment tree, with no values to read (`q_topology`).
- **Fig. 2(a)** (p. 6): read `fig2a_femoral_peaks` → datum `fig2a_femoral_peak_values`. These are the
  highest peaks of the two cycles, on the femoral (dash-dot) line, whose sharp peaks stand clear above the
  other lines. Calibration: x ticks at 0.5, 1.0, 1.5 plus the frame lines (misfit 1.3 px). The y ticks are
  bumps of a few pixels, so the centres of the labels 20 and 10 stand in for them, with the frame lines for
  30 and 0 (misfit 1.0 px). Result: 27.5 kPa at 0.51 s and 24.9 kPa at 1.53 s. No model in the record
  outputs femoral pressure, so this datum is not compared. It settles the "by eye" part of
  `q_eq4_not_runnable`: the plotted peak is above 2 p0 (`q_fig2a_femoral_peak`). The other three lines
  (ascending aorta, abdominal aorta, brachial) cross one another throughout, so they were not read.
- **Fig. 2(b)** (p. 6): read `fig2b_inflow` (the proximal boundary condition over the second pulse,
  1.22-1.42 s, as the topmost ink) and `fig2b_inflow_peaks` (the peak of each cycle). Data
  `fig2b_inflow_curve` and `fig2b_inflow_peak_values`, origin reported: this is an input of the model. Misfits
  are 1.7 px in both x and y. Peaks: 504 and 503 ml/s at 0.331 and 1.333 s. These are recorded, not compared,
  because the record's half-sine inflow is the reader's choice (`q_fig2b_inflow`, `q_inflow`). The
  backflow dip and the abdominal, brachial and femoral flows were not read: they cross one another and the
  dip near 0.5 s.
- **Fig. 3** (p. 6): read all three lines. Calibration: inward ticks at 20-80 % and at Q/Qn = 1, 3 (the
  2 tick is not found), and the frame lines for 0/100 % and 0/4 (misfit 3.6 px in x, 1.9 px in y).
  - `fig3_constant`: the solid line, constant distal resistance, traced along the lowest line near
    Q/Qn = 1, at 2-95 %. Compared at 90 % (`fig3_constant_at`, read 0.82 [0.80, 0.84]) with
    `run_fig3_constant`, a sweep of `arterial_tree_1d` without autoregulation (model 0.81;
    `cmp_fig3_constant`).
  - `fig3_reduced`: the dashed line, "Reduced Distal Resistance 0.2 x RT" (Elevated Flow), traced at 2-95 %.
    The trace is kept falling so it does not follow the label pointer. It is compared at 20 % (read 3.91) with
    `run_fig3_reduced`, which uses the new model `arterial_tree_1d_dilated`: `arterial_tree_1d` with the
    distal resistances at 20 %. The model gives 2.46 (`cmp_fig3_reduced`, `q_fig3_elevated_flow`).
  - `fig3_vasodilation`: the dotted line, each dot read at its centre where it stands clear of the solid
    line (71.8-93.2 %). The first three dots merge with the solid line and are not read. Recorded but not
    compared: the record's autoregulation holds Q/Qn at 1 by construction.
- **Fig. 4** (p. 7): read `fig4_s90` (90 % stenosis, dash-dot, the lowest line) and `fig4_s85` (85 %,
  dashed, the second lowest), each at 15-17 times over the two cycles. Data `fig4_s90_curve` and
  `fig4_s85_curve`. No y tick marks can be found, so the centres of the labels 25-0 are used, with misfit
  2.1 px. The intervals are widened by 15 px (0.27 kPa) for the unknown offset between a label and its tick
  (`q_fig4_calibration`). The normal, 60 % and 75 % lines overlap and cross and are left out. No model in
  the record outputs a posterior tibial pressure waveform, so these readings are not compared.
- **Fig. 5** (p. 7): left out. The five flow lines (normal, 60, 75, 85, 90 %) overlap and cross along
  almost the whole cycle: the 85 % and 90 % lines meet the others at the peaks, at the backflow and in
  diastole. No line can be followed on its own over a useful range, and no model output in the record is a
  flow waveform.
- **Fig. 6** (p. 8): read `fig6_distal` (solid line, distal to the stenosis) and `fig6_ankle` (dashed line,
  ankle) at 2-90 %. The two coincide up to about 75 %, where both readings take the shared line. Beyond
  that the solid line is traced along the lower edge of the ink and the dashed line along the upper edge.
  Calibration: all inward ticks plus the frame lines (misfit 3.7 px in x, 2.7 px in y). Compared at 80 %
  (read 0.69 and 0.70) with `run_fig6_fig9`, the autoregulated femoral-stenosis run (segment 46,
  Ls = 2 cm), which gives 0.46 and 0.44 (`cmp_fig6_distal`, `cmp_fig6_ankle`, `q_fig_stenosis_ratios`).
  The falling ankle line settles which side the legend means (`q_fig6_side_figure`). The paper's claim that
  "a PI ratio of 0.2 requires a stenosis with severity greater than 90%" is consistent with the reading:
  both lines are still at 0.42-0.48 at 90 %.
- **Fig. 7** (p. 8): left out as a figure. These are flow pulses redrawn from Gosling et al. (1971),
  drawn without axes. Their printed PI labels are already data (`PI_*_gosling`).
- **Fig. 8** (p. 9): read `fig8_thigh`, `fig8_knee` and `fig8_ankle` at 2-55 %, where the three flat
  lines lie apart (top = knee, middle = ankle, bottom = thigh; `q_fig8_legend`), and `fig8_band` at
  60-94 %, where they meet and cross and are read as one band (`q_fig8_band`). Calibration: the short
  inward ticks at every label (misfit 2.7 px in x, 3.8 px in y; the printed tick spacing is itself uneven by
  a few px). Compared at 30 % (read 1.11, 1.15, 1.12 for thigh, knee, ankle; model 1.19, 1.29, 1.29) and,
  for the band, at 80 % (band 0.85-0.90; model 0.79, 0.80, 0.78). The runs are `run_fig8_flat` and
  `run_fig8_band` (autoregulated abdominal stenosis), compared in `cmp_fig8_thigh`, `cmp_fig8_knee`,
  `cmp_fig8_ankle` and `cmp_fig8_band_*` (`q_fig_stenosis_ratios`).
- **Fig. 9** (p. 10): read `fig9_thigh`, `fig9_knee` and `fig9_ankle` at 2-50 % (flat lines apart: knee
  on top, ankle in the middle, thigh at the bottom) and at 67-85 %. In that range the solid thigh line is
  the top one and rises, the dashed knee line is above the dash-dot ankle line, and each is traced from
  the first column near 65 % where all three show ink. The crossing region (55-65 %) and the bunched ends
  beyond 85 % are not read. Misfit 2.8 px in x, 4.4 px in y. Compared at 80 % (read 1.14, 0.89, 0.86 for
  thigh, knee, ankle; model 1.36, 0.77, 0.76) with `run_fig6_fig9`: `cmp_fig9_*` (`q_fig_stenosis_ratios`).
- **Fig. 10** (p. 10): left out. The aortic and femoral pressures for normal flow and severe aortic stenosis
  are four lines that cross repeatedly. The record cannot model this case: its input is an aortic pressure
  waveform that is only plotted. Only the normal femoral peak stands clear, and with no model to compare it
  with, it was not read.
- **Fig. 11** (p. 11): left out, for the same reasons as Fig. 10 (aortic and radial pressures, four
  crossing lines).
