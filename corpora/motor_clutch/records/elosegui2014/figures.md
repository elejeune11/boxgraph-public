# Figures of elosegui2014

Second pass, 2026-11-01. The first reading recorded no figure (the rendering commands
were refused then); this pass reads every data panel of the article with calibrated readings in
`figures.yaml`, each by its own code (`figures/<id>.py`, which calls the shared `figures/_kit.py`, whose
docstring gives the method and how each interval is made). The Supplementary Information (PDF pages
8-34) renders blank in this copy, so none of its figures could be seen.

All plots are vector drawings, rendered at 1200 dpi (Figs. 1-3) or 1600 dpi (Fig. 4). The y axis is
always calibrated from its own tick marks matched to the printed labels (misfit 0.2-0.5 px). Error bars
are SEM in every figure (each caption says so). Overlays from `boxgraph figure check` are in
`figwork/<id>.png` (not committed).

How the x positions are handled. Fig. 1 and Fig. 2a have x ticks (misfit 0.2 px). Figs. 3c-e and 4d-i
have no x ticks, and their printed labels 0.1, 1, 10, 100 are not on one log scale (q_fig34_x_labels):
in Fig. 4d-i the '1' and '10' labels sit left of the dashed regime lines, while in Fig. 4j-l (ticks at
0.1 and 100) the dashed lines fall where 1 and 10 kPa are. So every measured circle is named by its gel,
taken in order from the left among the gel stiffnesses printed in Fig. 1a (0.25, 0.7, 2, 2.8, 5, 14,
29 kPa), and each model line of Fig. 4 is read at the column of the measured circles it is compared with.
Fig. 3 has no circles: its curves are read at x from the label centres (log fit, misfit 59 px), and each
interval spans the curve over x +- twice that misfit, which makes the steep parts wide.

## Fig. 1 (p. 2)
- 1a: traction colour maps: left out, no values to read (the colour bar gives traction, but a map has no
  single value per cell to compare).
- 1b: read. `f1b_ctrl` (red, myo ctrl, 7 gels) and `f1b_b6` (blue, myo b6, 7 gels): marker centres and
  both ends of each vertical SEM bar; x and y from ticks (misfit 0.2 / 0.3 px). Bars hidden in their
  marker (red 0.25 kPa, blue 0.25 kPa) are at most the marker. `f1b_ctrl_sub` is the same red circles at
  the four gels visible in Fig. 4d, for the replot comparison.
- 1c: read. `f1c_ctrl_ab` (red, 7 gels) and `f1c_b6_ab` (blue, drawn under the red; 6 gels: the 0.7 kPa
  blue circle is wholly hidden). Hidden bar ends are mirrored, as the overlay notes say.

## Fig. 2 (p. 3)
- 2a: read. `f2a_a5b1_264` (the bold blue curve) and `f2a_avb6_264` (the lower bold salmon curve, the one
  ending at the salmon '264 nM' label; there are two bold salmon curves, q_fig2a_two_bold), at 40-80 s and
  100-130 s; the vertical steps at 30 and 90 s are not read. The y axis 0 tick is covered by the curves'
  start: calibrated from 20-80 (misfit 0.2 px). The interval is half the bold line's width. The thin
  curves (other concentrations) are left out: the caption gives their range of concentrations but not
  which line is which. The dissociation timescale bears on q_koff_column_multiplier (q_fig2a_koff_timescale).
- 2a table: already in data.yaml (kont, koff).
- 2b: read. `f2b_a5b1_ctrl`, `f2b_a5b1_b6`, `f2b_avb6_b6`: bar tops (centre of the top outline) and
  the upper SEM end (lower end hidden by the bar, mirrored); misfit 0.2 px. These are the bars behind
  the printed 'fivefold' (density_ratio_fivefold), but no comparison is recorded: a run can only sweep a
  model over a figure datum's x positions, not take its values as inputs, so the ratio of two bars
  cannot be formed in this record (the unused `models/density_fold` was written for it). Axis printed
  'Integrins (um2)' (q_fig2b_axis_unit).
- 2c top: micrograph, left out. 2c bottom: read. `f2c_detach`, the five drawn bars (black and coloured;
  conditions 1, 2, 5, 6, 7); conditions 3, 4 and 8 have no bar drawn and are not read. Misfit 0.5 px.
- 2d, 2f: micrographs, left out.
- 2e, 2g: read. `f2e_b1`, `f2g_b6`: four bars each with their SEM; misfit 0.5 and 0.2 px.

## Fig. 3 (p. 4)
- 3a, 3b: model schematic and flow of events, left out (drawings).
- 3c, 3d, 3e: read. `f3c_model`, `f3d_model`, `f3e_model`: the model curve, traced from a seed, at the
  gels compared with Fig. 4 (3c at all 7, 3d at the 5 of Fig. 4f, 3e at the 4 of Fig. 4e). All three are
  cut from one crop of the stacked panels; the shared x labels are under 3e (misfit 59 px, see above).
  `cmp_fig4d_fig3c`, `cmp_fig4f_fig3d`, `cmp_fig4e_fig3e` compare them with the a5b1 lines of Fig. 4.
  These are the model predictions the record cannot run (q_si_unreadable); they are recorded as
  predicted data. On q_fig3d_onset_vs_14kPa: see q_fig4_onset_below_14kPa.

## Fig. 4 (p. 5)
- 4a: traction maps, 4b: actin micrographs and kymographs, 4c: integrin staining micrographs: left out
  (no values to read).
- 4d: read. `f4d_filled` (myo ctrl; visible at 0.7, 2, 14, 29 kPa; the others are under open circles),
  `f4d_open` (myo b6 + avb6 ab, 7 gels; `f4d_open_sub` the same at the 6 gels visible in Fig. 1c), the
  model line `f4d_line` (at the open circles) and `f4d_line_ctrl` (at the filled ones). Open circles are
  found as rings, filled ones as disks; the line is the light-blue mask after blanking the circles with
  their horizontal bars and removing the thin error bars by an opening, traced and interpolated across
  the blanked columns (the interval covers the rows on both sides of the gap).
- 4e: read. `f4e_pts` (4 gels) and `f4e_line`.
- 4f: read. `f4f_filled` (visible at 0.7, 14, 29 kPa), `f4f_open` (5 gels), `f4f_line`, `f4f_line_ctrl`.
- 4g, 4h, 4i: read. `f4g_pts`/`f4g_line` (7 gels), `f4h_pts`/`f4h_line` (4), `f4i_pts`/`f4i_line` (5).
- 4j, 4k: read. `f4j_pts`/`f4j_line` (7 gels), `f4k_pts`/`f4k_line` (4).
- 4l: read. `f4l_b1` (blue, 5 gels), `f4l_b6` (orange, 4 gels; the 5 kPa one is under the blue circle),
  `f4l_b1_line` (the thick blue line; the thin orange line runs along it below 7 kPa, so the blue mask is
  closed vertically to join its two strips), `f4l_b6_line` (orange line, read only at 14 and 29 kPa,
  where it is apart from the blue line; `f4l_b6_hi` are the orange circles there).
- Comparisons: every model line against the circles it is drawn through (`cmp_fig4*_line*`,
  validation), and the replotted measurements against Fig. 1 (`cmp_fig1b_ctrl_fig4d`,
  `cmp_fig4d_b6ab_fig1c`, `cmp_fig1b_b6_fig4j`, consistency).

## Error bars and hidden marks
Most Fig. 4 circles carry SEM bars smaller than the circle on the soft gels; those are reported as at
most the circle. A bar end hidden behind another mark is taken as the mirror of the visible end, and the
outer interval spans both (notes in each reading). Points wholly hidden are not read (q_fig4_hidden_points).
Where bars of one colour overlap (Fig. 4d and 4f at 14 and 29 kPa, filled and open circles one above the
other) a stem may be followed into the neighbour's bar or stopped where the model line crosses it; on
the overlay the upper end of the open 14 kPa circle in Fig. 4d is read at the line crossing, below the
cap the eye sees, so that SEM bar is under-read.
