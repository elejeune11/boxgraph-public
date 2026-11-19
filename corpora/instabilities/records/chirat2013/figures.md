# Figures of chirat2013

The earlier pass digitized no figure. This pass reads the two Fig. 4 panels, which are vector plots with
numbered axes, with the record's own reading code (`figures/`). It also records the tick values printed on
the Fig. 5 axes as data. Fig. 3 is left out (see below).

- **Fig. 1 (p. 2), A-D**: left out. These are photographs of shells with scale bars. No values are plotted, and no
  spine count or size is given against a model.
- **Fig. 2 (p. 2)**: left out. It is a drawing of the model set-up, with no values.
- **Fig. 3 (p. 3), three panels (g = 1, 4, 8)**: left out.
  - The panels are a low-resolution raster even at 1200 dpi: the y tick labels and tick marks on the central
    axis are illegible blurs, so the y axis cannot be calibrated from the image.
  - Each panel overlays dozens of curves, one per growth increment, with no stated growth times. Only the
    outer envelope can be told apart.
  - By eye, the final spine heights fall in the order the text states (taller at lower g): about 1.0, 0.85 and
    0.47 for g = 1, 4 and 8. This is not a calibrated reading and is not entered as data.
- **Fig. 4 left (p. 3), "Mantle stiffness" Eb(s0)**: read as `fig4_left_Eb` (datum `Eb_profile_fig4`,
  predicted). This is the grey curve, solid and dashed; the black b1 and b2 arrows are excluded.
  - Calibration: from the image, at 1200 dpi.
    - The axes are the longest black lines.
    - Five major x ticks are matched to 0.2 to 1.0.
    - Six major y ticks are matched to 0.5 to 1.0.
    - Ticks are told apart from the curve by grey level (black at about 35, curve at about 93 to 122).
    - Misfit is 0.0002 on both axes.
  - Points: 14 s0 positions from 0.1 to 0.9. s0 = 0.5 is skipped because the b1 arrow covers it. The 95%
    intervals are 0.002 to 0.005 (line thickness and slope).
  - Comparison: compared with Eq. 1 (`stiffness_profile_eq1`, run `run_Eb_fig4`, comparison `cmp_Eb_fig4`).
    b1 = 0.5 and b2 = 0.0707 are added inputs taken from the figure itself.
  - Result: the drawn curve is a Gaussian of standard deviation 0.1 to within the reading's precision. This
    answers q_fig4_readable. The meaning of b2 is raised in q_fig4_b2_meaning: the arrow labelled b2 marks
    about the half width at half depth.
- **Fig. 4 right (p. 3), "Deformed mantle shape" y(x)**: read as `fig4_right_shape` (datum `shape_fig4`,
  predicted). This is the grey curve; the pointing hand and axes are excluded.
  - Calibration: from the image.
    - Six major x ticks are matched to 0.0 to 1.0, skipping the y axis column.
    - Four equally spaced major y ticks are matched to 0.1 to 0.4. Only 0.2 and 0.4 are labelled; the misfit
      of 0.0001 confirms the equal spacing.
    - x misfit is 0.0002.
  - Points: 18 x positions. Near the tip the 95% intervals are 0.001 to 0.007.
  - The curve is symmetric to within 0.0005, with a tip height of about 0.386 near x = 0.5 and shallow dips of
    about -0.009 near x = 0.15 and 0.85.
  - Not compared: it is an output of the non-runnable growth simulation, whose inputs for this panel are not
    stated (q_fig4_shape_uncompared).
- **Fig. 5 (p. 4), phase diagram**: no reading.
  - The four panels are 3D renderings and shell photographs with no value axes of their own.
  - The axes do print tick values, now recorded as data from the tick labels (vector text missing from the
    OCR): b1 = 0.85 and 0.25, g = 0.5 and 2.5 (`b1_fig5_upper`, `b1_fig5_lower`, `g_fig5_left`, `g_fig5_right`).
  - These settle part of q_sim_inputs, which said Fig. 5 shows no axis values (see q_fig5_axis_values).
- **Fig. 6 (p. 4)**: left out. These are schematic time evolutions with and without self-contact, with no axes.
- **SI (p. 7)**: there are no figures.
