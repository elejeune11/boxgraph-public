# Figures of radja2019 (first figure pass, 2026-11-14)

All readings are by the record's own code (`figures/`), checked with `boxgraph figure check`;
the overlays put every mark on the line, dot or peak meant.

- **Graphical abstract (p. 1)**: left out. Drawings of the pattern and a cross-section with one TEM
  image; no axes, no values.
- **Fig. 1 (p. 3)**: left out. Pairs of SEM micrographs and simulated surfaces. The values behind
  them (l0, u, percent difference) are printed in Table 1, which the record already holds.
- **Fig. 2 (p. 4)**: left out. SEM micrographs and rendered simulations (kinetic arrest), with no
  axes. Their parameters are in the caption and in the `conserved_dynamics_eq7` model. The caption's
  claim about wavelength order cannot be measured from the images (question `q_fig2_wavelength_order`).
- **Fig. 3 (p. 5)**: left out. Schematic, TEM and SEM images of P. incarnata development; only
  scale bars, no plotted values.
- **Fig. 4 (p. 6), phase diagram**: read: `fig4_boundary_a`, `fig4_boundary_b`. These are the two
  solid vertical boundary lines, each read at u = -0.9, -0.6, -0.3, 0.3, 0.6, 0.9. Calibration
  comes from the image: the 7 l0 tick marks (3 to 6), misfit 0.012 in l0, and the 3 u tick marks
  (1, 0, -1), misfit 0.005. The 95% interval is ±0.023 in l0 (line width plus misfit plus one
  pixel). Results:
  - Line a is at l0 = 3.548 at every u and runs unbroken from u = 1.08 to -1.04. Through
    `boundary_position` it is compared with the caption's "between l0 = 3.5 and l0 = 3.6"
    (`cmp_fig4_boundary_a`).
  - Line b is at l0 = 4.446, broken at u = 0. No printed value states its position, so it gets
    no comparison.
  - The caption's u extent "from u = 0.1 to u = 1.0" is recorded as question
    `q_fig4_boundary_extent`.

  The coloured state dots themselves are left out. They are categorical: one pattern geometry per
  computed (l0, u) grid point, every 0.1 in l0 and about 0.1 to 0.2 in u. No number can be read
  from them, and Eq. 6 is not runnable in the record (`q_eq6_not_runnable`). The legend's rendered
  shapes are drawings.
- **Fig. 5 (p. 9), family tree with state dots**: read: `fig5_orange`, `fig5_pink`, `fig5_green`,
  `fig5_blue`. These are measured data: the paper's categorization of the species of each family.
  - Method: each dot is found by colour (hue band, saturation > 0.3). Touching dots are split at
    the maxima of the distance transform. Each dot is placed by its angle about the tree centre,
    which is a least-squares circle through all 289 dots (the misfit puts about ±0.1° on each
    angle).
  - Dots per colour: orange 27, pink 42, green 75, blue 145.
  - `tree_state_counts` groups the dots by angle into terminal taxa, and these are compared with
    the printed counts. The figure gives 27 families with an equilibrium state (printed 27), 7 with
    only that state (printed seven) and 20 mixed (printed 20).
  - The figure has 195 terminal taxa with dots, against the printed 205, and therefore 168 families
    without an equilibrium state, against the printed 178 (question `q_fig5_tip_count`).
  - The bottom legend panel is a drawing with no values. It does show how the 3-state model's states
    C/D/E are built from the dot colours, which bears on `q_state_categories` (new question
    `q_state_categories_fig5`).
- **Fig. S1 (p. 22), GC chromatogram, composition**: read: `figS1_peaks`. This is a measurement.
  - Method: the apex (retention time, abundance) of every peak more than 1e5 above the axis. The
    raster screenshot is calibrated on its printed labels: 12 time labels (misfit 0.02 min) and 13
    abundance labels (misfit 1.1e4). The trace is the dark connected set that contains the axis line.
  - Peaks read: 23.43, 25.07, 27.66, 28.49 (4.7e6), 30.79, 31.39 (1.2e6) and 37.33 min (Inos, 6.3e6).
  - The first Glc peak (about 27.4 min) runs off the top of the plot, so its height is not shown.
  - Before 14.6 min the "Ara" labels touch the trace. Neither region is read.
  - No model in the record uses these values. The peak labels name sugars and are not read, and
    Table S2's mol % (not entered) is the paper's own reduction of this trace.
- **Fig. S2 (p. 23), GC chromatogram, linkage**: read: `figS2_peaks`, the same way, with a
  threshold of 1.5e5.
  - Calibration: 10 time labels (misfit 0.005 min) and 8 abundance labels (misfit 2.8e4).
  - Peaks read: 13.00 (t-Glc, 1.61e7, at the top of the scale), 17.28 (4-Glc, 4.2e6), 15.70, 16.87
    and smaller peaks.
  - The labels "t-Araf" (about 10.3 min) and "2-Rha"/"t-Man" (12.6-12.95 min) touch the trace, so
    those peaks are not read.
- **Fig. S3 (p. 24), detailed tree**: left out as a reading. It shows the same character-state dots
  as Fig. 5, but with every family name printed in coloured text in the same hues as the dots, so a
  colour mask cannot separate dots from names. Fig. 5 carries the same data and was read instead.
