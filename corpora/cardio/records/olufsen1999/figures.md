# Figures of olufsen1999

Read by the record's own code (`figures/*.py`, shared code in `figures/_common.py`, `_fig9.py`,
`_dashes.py`, `_fig12.py`). Every reading was checked with `boxgraph figure check`: on the overlays every
mark sits on the intended line or marker.

## Read

- **Fig. 3** (p. 3), `fig3_fit`: the solid 'fit' line (Eq. 6) at 11 radii; r0 = 0.06 and 0.13 left out
  (markers touch the line there). Calibrated on the frame and bottom/left ticks matched to the printed labels.
- **Fig. 3** (p. 3), `fig3_data`: the '+' markers (Eh/r0 estimates), 103 found; a few overlapping markers
  in the dense cluster near r0 ≈ 0.08 cm may be merged. Legend excluded.
- **Fig. 4** (p. 3), `fig4_inflow`: inflow q(t), first period: the rescaled, smoothed measured inflow
  (ref. 20), the input to the 1D model.
- **Fig. 9(B)** (p. 9), `fig9b_st`: solid s.t. line, |Z|, read only at omega < 4 and > 65 1/s, where
  it is the only black line.
- **Fig. 9(C)** (p. 9), `fig9c_st`: solid s.t. line, phase, read only at omega < 1 and > 65 1/s.
- **Fig. 9(B)**, `fig9b_md0` (dash-dot md 0, omega 10-20 and 40 1/s) and `fig9b_md1` (dashed md 1,
  omega 7-20 and 38-45 1/s): the measured |Z| (second pass). Calibration as for the s.t. line (decade
  ticks 10^0-10^2 and the right frame at 10^3; y frame ends 10^4 and 10^2, checked by the 10^3 tick):
  x misfit 0.95 px, y misfit 3.5 px. The solid line is removed by tracing, dots are dropped by size,
  and the remaining dashes are grouped into tracks; md 0 and md 1 are told apart by their order
  (below the solid line for omega 7-20, md 1 lowest; for omega 38-45 md 1 above md 0), which matches
  their line styles in the overlay. Where a column falls in a gap, the value is interpolated between
  the neighbouring dashes (the measured curves are straight segments between points). Each interval
  adds the line half-width, the misfit and the spread of the dash extensions.
- **Fig. 9(C)**, `fig9c_md0` (omega 3-3.5 and 9-16 1/s) and `fig9c_md1` (omega 1-3.5 and 7-12 1/s):
  the measured phase (second pass), same method; x misfit 0.75 px, y misfit 3.5 px. Positions where
  the tracks touch or a third track appears (omega 4, 14 and the steep rise above 20 1/s) give no value
  and were left out.
- **Fig. 12(A)** (p. 11), `fig12a_aortic`: the thick 'Aortic' line (measured, ref. 41) on its upstroke
  (t -0.02 to 0.06 s) and from its fall after the peak through the incisura (t 0.24-0.36 s). The plot has
  only a left and a bottom axis: ticks found on both; x fitted to the ticks 0-.7 (the first tick,
  printed '-0.3', sits at -0.03 s: `q_fig12_time_label`), y to 80, 90, 100, 110, 130 (the 120 tick is not
  found in the scan). Misfit x 13.8 px (uneven tick spacing of the scan), y 7.7 px; the intervals add the
  local slope times the x misfit. The thick line is isolated by a morphological opening whose radius is
  set from the ink widths of the image, keeping only the widest linked piece.
- **Fig. 12(B)** (p. 11), `fig12b_0cm`: the thick '0 cm withdrawal' line (measured) on its upstroke
  (t 0.03-0.06 s) and its flat top (t 0.13-0.17 s); x fitted to 0-.7, y to the labelled ticks 80, 100,
  120, 140; misfit x 8.1 px, y 6.2 px.
- **Fig. 12(B)**, `fig12b_radial`: the 'Radial' curve around its peak (t 0.17-0.22 s), where it is the
  uppermost line by far; columns pooled over ±8 px to bridge its dots, which widens the interval by the slope.

Comparisons made from these readings: the s.t. readings against the tree built from the printed
inputs (reproduction; see `q_fig9_magnitude`), and the measured md 0 / md 1 readings against the same
tree (validation; `val_tree_*`). The measured curves follow the plotted s.t. line at omega 5-25 1/s but
not the tree from the printed inputs; this supports `q_fig9_magnitude` without settling it
(`q_fig9_measured_vs_tree`). The Fig. 12 measurements have no model in the record that predicts them
(the 1D model is not runnable); they are recorded for later models.

## Left out

- Fig. 1, 2, 5, 6: drawings.
- Fig. 7 (pressure-flow loops, 5 per panel): closed p-q loops traced in time, not functions of q, which
  overlap and cross near the origin; output of the non-runnable 1D model (`larger_arteries_1d`).
- Fig. 8 and Fig. 10: 3D mesh surfaces p(x, t) in perspective; no axis plane on which values can be read.
- Fig. 9(A): the same curves as 9(B) on linear axes, where the measured and s.t. curves lie on top of
  each other below 60 1/s; 9(B) and 9(C) are read instead.
- Fig. 9 windkessel (dotted) curve: its parameters are fitted and not printed, so no model here runs it.
- Fig. 9 measured curves outside the stretches listed above: there they cross each other and the solid
  line (omega about 4-7 1/s in B, 20-60 1/s in B and C).
- Fig. 11 (6 and 5 thin curves, two of them solid in each panel): the curves cross each other over
  the whole cycle and the two solid ones cannot be told apart by style; output of the non-runnable 1D model.
- Fig. 12 curves other than those read: the thin withdrawal curves (A: 0-30 cm, B: 30-70 cm) overlap
  in dashed, dotted and dash-dot styles of similar weight throughout; the thick lines and the radial peak
  are read only where they are apart from them.
