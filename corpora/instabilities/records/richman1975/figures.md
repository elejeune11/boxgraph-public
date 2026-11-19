# Figures of richman1975

Read by code from the page at 1200 dpi (figures.yaml; code in `figures/`). Only Fig. 4 plots values.
The paper has no plotted measurements: its measurements are in Table 1 and the text (already in data.yaml).

- **Fig. 4A (p. 3)**: read as `fig4a_l_over_t` (datum `l_over_t_fig4a`, origin predicted), the
  single curve of l/t against sigma2/sigma1, at 18 x values from -1 to 1 (x = 0 is left out because
  the y axis hides the curve there). Calibration: from the image, the x ticks on the axis line matched to the
  printed -1, -.75, ..., 1 (the y axis line is the 0 mark), and the y-axis crosses matched to 2, 4, 6, 8.
  The hand-drawn axes lean by a few pixels, so values are read along lines parallel to the drawn axes.
  Misfit: 5.7 px in x (tick spacing about 294 px, unevenly drawn), 4.8 px in y (about 290 px per unit).
  The interval is the curve's ink over the columns the x misfit allows, plus the y misfit: about ±0.04 on
  the plateau and up to ±0.6 on the steep part near -0.85. Overlay checked: every mark is on the curve.
  Run `run_plate_fig4a` / comparison `cmp_plate_fig4a` test the thin-plate reading `plate_on_foundation`
  (constant l/t ≈ 9.4) against it. Findings: the plateau lies at about 7.8, below the "8" tick
  (q_fig4a_plateau_below_8). The reading answers the open question q_microgyric_l_over_t_not_modelled
  in part: l/t ≈ 1 sits near sigma2/sigma1 ≈ -0.9 on a steep part of the curve (q_fig4a_microgyric_l_over_t).
- **Fig. 4B (p. 3)**: read as `fig4b_sigma_crit` (datum `sigma1_crit_fig4b`, origin predicted), the
  single curve of (sigma1)critical/E1 against sigma2/sigma1, at 20 x values from -0.7 (the curve begins
  near -0.72) to 0.95 (it ends at about 1). Calibrated the same way, on x ticks -1 ... 1 and y ticks .2, .4, .6, .8.
  Misfit: 4.6 px in x and 4.6 px in y (about 2950 px per unit); intervals about ±0.005 to ±0.02.
  Overlay checked: every mark is on the curve. Run `run_plate_fig4b` / comparison `cmp_plate_fig4b` test
  `plate_on_foundation`; it gives about 0.8 of the plotted value for sigma2/sigma1 >= 0
  (q_fig4_thin_plate_mismatch). This is the curve behind the claim that buckling needs sigma1 above a
  critical value (lissencephaly, p. 4).
- **Fig. 1A, 1B (p. 2)**: left out: micrographs (microgyric and lissencephalic cortex) with 1 mm scale
  lines; no plotted values. The caption's "intergyral wavelength approximately equal to the cortical
  thickness" is a qualitative observation.
- **Fig. 2 (p. 3)**: left out: camera lucida drawings of cytoarchitecture, no values.
- **Fig. 3A, 3B (p. 3)**: left out: schematics of the two-layer sphere and of the symmetric buckled
  surface (lx = ly = l√2), no values.
