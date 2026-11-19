# shyer2013: figure readings

Figure pass of 2026-11-18. All readings run code (`mode: code`) from `figures/`; the shared logic is in
`figures/_shyer.py`, and each reading file holds only its CONFIG (colours, tick labels, marker kind).
Calibration always comes from the image: tick marks found on a spine and matched in order to the
printed labels (labels printed at a box corner are matched to that spine). The largest calibration
misfit (px) is carried into every interval. Each reading was checked with `boxgraph figure check`
and its overlay (`figwork/<id>.png`) inspected: the marks sit on the meant markers, bars and lines.

Figs. 4B and 6C are both embedded raster images. Fig. 4B is JPEG-like at roughly 300 dpi, 6C is
cleaner. Both are rendered at 1200 dpi. Figs. 2 and 3 are spreadsheet-style charts with thick gray
axes. The SM figures are low-resolution scans.

## Read

- **Fig. 2B (p. 2), bars**: `f2b_ratio` (datum `circ_ratio_fig2b`), 5 bars E8-E12. The value axis
  comes from the 5 gray ticks protruding left of the thick left spine (0.5-2.5, misfit 0.7 px). A bar's
  value is the centre of its gray top outline stroke, found from the solid cyan fill's top edge
  (5th percentile of the column tops, so the green marker and line drawn over the E8 and E9 bars do not pull it
  down) less half the stroke width. Error bars are hidden in the outline and reported as at most the
  outline. **The bars belong to an unlabelled right axis; they are read on the left labels**
  (q_fig2b_ratio_axis). Mean 0.571 against the text's 0.55: `cmp_mean_fig2b` not reproduced.
- **Fig. 2B, lines**: `f2b_mes` (blue squares, outer circumference of the separated mesenchyme and
  endoderm, 1.09-2.15 mm) and `f2b_muscle` (green circles, muscle inner circumference, 0.50-0.98 mm).
  Each marker's centre is what survives a disc opening that removes the thick connecting line. No
  error bars are drawn.
- **Fig. 2D (p. 2), top right**: `f2d_ratio`, 3 bars DMSO/AG/FK (categories 1-2-3), ticks 0.5-1.5
  (misfit 1.0 px). The error bars on AG and FK are hidden in the outline. The mean of AG and FK is 0.538
  against the text's 0.53: `cmp_mean_fig2d` close (model `mean_culture_circ`).
- **Fig. 3A (p. 3), right**: `f3a_ratio`, 4 bars E12-E15: 1.04, 0.74, 0.69, 0.55. The error bars are
  read as the gray stub above the outline (upper end) and the stub into the fill (lower end). They
  agree with the text's ≈ 0.75, 0.69, 0.55 (approximate values, so no verdict). They give no separate
  endoderm ratio, so q_zigzag_ratios_source stays open.
- **Fig. 3C, 3D (p. 3), top right**: `f3c_ratio`, `f3d_ratio`, 3 bars each, error bars read. The means
  over AG and FK are 0.663 (against 0.66, `cmp_mean_fig3c` reproduced) and 0.686 (against 0.68,
  `cmp_mean_fig3d` close).
- **Fig. 4B top left (p. 4)**: circumferences, y calibrated on the right spine's ticks 0.5-2 plus 0 at
  the bottom spine, x on the E8-E14 ticks (misfits 0.5 px).
  - `f4b_circ_endo_meas` (red filled circles, E7, E8, E10, E12, E13, E14) has 1 SD bars. The E10 bar is
    crossed by blue ink, so the walk bridges 12 px gaps there.
  - `f4b_circ_endo_sim` (red open circles, E7-E14). The E14 ring is partly covered and is located by
    ring-template search, with its interval doubled.
  - `f4b_circ_musc_meas` (blue filled circles) leaves out E10, hidden under the red markers.
  - `f4b_circ_musc_sim` (blue open circles) has E10-E13 only: E8 and E14 are under the filled markers
    and E9 is under a red ring.
- **Fig. 4B top right**: `f4b_spacing_meas` (λ/he measured, 5 points with SD bars) and
  `f4b_spacing_sim` (6 points; E10 is under the filled marker).
  - `f4b_stressfree` is the dotted pink line, the stress-free (he + hm)/he. It reads 3.98-3.99 at
    E8-E14. Against the chick schedule run over the same days (`run_chick_stressfree_fig4b`, exactly 4),
    `cmp_stressfree_fig4b` is reproduced.
- **Fig. 4B bottom left**: down-triangle markers, positioned half-way between the bounding-box centre
  and the circumcentre, with that spread added to the interval.
  - `f4b_long_meas` (red, E12-E14, SD bars) gives 1.02, 0.75, 0.69. E13 is separated from the
    overlapping simulated triangle by keeping the lower marker of the merged blob.
  - `f4b_long_sim` covers E7-E12. Its E12 triangle reads as filled (its hole is closed in the raster)
    and is picked as the lower of the two red markers there. E13 and E14 overlap the measured markers
    and are not read.
  - `f4b_circ_ratio_meas` (blue, E8-E12, SD bars) averages 0.551 against the text's 0.55:
    `cmp_mean_fig4b` reproduced.
  - `f4b_circ_ratio_sim` covers E7 and E9-E14; E8 is under the filled marker.
- **Fig. 4B bottom right**: `f4b_mu_endo` (690, 687 Pa; its pale-pink SD bars are read in a pink mask)
  and `f4b_mu_mes` (66, 52 Pa, lilac bars), on the left axis 0-800. `f4b_mu_ratio` is the purple
  triangles on the right axis 0-20: 10.6 at E8 and 13.1 at E10. The ratio of the plotted moduli
  (`run_mu_ratio_fig4b`: 10.5, 13.3) against the plotted ratio gives `cmp_mu_ratio_fig4b` close; a
  mean of ratios need not equal a ratio of means.
- **Fig. 6C left (p. 6)**: `f6c_circ_endo_meas` and `f6c_circ_musc_meas` (E12.5-E15.5, SD bars),
  `f6c_circ_endo_sim` (E13.5-E15.5; E12.5 is under the filled marker) and `f6c_circ_musc_sim`
  (E12.5-E15.5).
- **Fig. 6C middle**: `f6c_spacing_meas` (3.0, 3.5, 6.5 with SD bars) and `f6c_spacing_sim` (3.8, 5.5,
  6.7).
  - `cmp_spacing_fig6c` (validation, simulation against measurement) is close: E14.5 is about three SD
    off (q_spacing_fig6c).
  - `f6c_stressfree` is the red dotted line, read as the lowest red ink at each x, 2.28 to 3.02. The
    printed mouse schedule (`run_mouse_stressfree_fig6c`) gives 2.33 to 3.00: `cmp_stressfree_fig6c`
    close, with the middle of the line lower than the schedule (q_stressfree_fig6c).
- **Fig. 6C right**:
  - `f6c_mu_endo` reads 121 Pa and `f6c_mu_mes` 79 Pa, both with SD bars. The left axis has ticks at
    50 and 100, 0 at the bottom and 150 at the top, with a 0.8 px misfit.
  - `f6c_mu_ratio` reads 1.55 on the purple right axis. That axis's very short, light ticks are found
    with a 2 px minimum length, and are unevenly placed (misfit 7 px, carried).
  - `cmp_mu_ratio_fig6c` (121/79 = 1.53) is reproduced.
- **Fig. S6(b) (p. 20)**: `fs6b_ratio` reads the 8 open circles, G/G0 against opening angle.
  - The scan is tilted 0.12 degrees and is straightened with `boxgraph.digitize.deskew`. The light-gray
    axes are calibrated on the 50-250 ticks plus the 0 and 300 corners, and 1.0 plus the 0.5 corner
    (misfits about 1 px).
  - The x positions read (24.1, 47.5, 94.7, 139.9, 183.1, 223.5, 259.9, 291.9) match the angles
    printed in the caption of Fig. S4 (24.3-292.1 degrees), which checks the calibration.
  - G/G0 = 1.16 at 292 degrees bears on the SM's 'around 15%' (`modulus_increase_292`, printed ≈, so
    no verdict).
- **Fig. S6(a) (p. 20)**: `fs6a_noeigen` reads the 41 green filled squares of the 'Without Eigenstrain'
  curve that are not covered by the eight opening-angle curves. The legend's sample square is excluded
  by its layout box. The calibration (0-180 µm, 0-0.14 µN) uses the deskewed crop.

## Bearing on open questions

- **q_plotted_measurements**: answered by this pass. The plotted moduli, circumferences, spacings and
  ratios are now readings (data `*_fig2b` … `*_fig6c`). They can serve as inputs and validations for
  the wrinkling laws of huang2005, cerda2003 and tallinen2015: modulus ratio about 10.6-13.1 in chick
  and 1.5 in mouse, λ/he 6.6-10 in chick and 3.0-6.5 in mouse.
- **q_modulus_ratio_values**: the measured chick ratio is 10.6 at E8 and 13.1 at E10, with a mean of
  about 11.9. So the simulations' 12 sits between the two measured values. The text's 'about 10' and
  'more than 10' are rounder statements of the same data.
- **q_circ_ratio_sim_vs_measured**: Fig. 4B's simulated circumferential ratio of muscle to separated
  composite (`f4b_circ_ratio_sim`) is 0.58 at E7 and 0.50-0.52 from E10 to E14. That is close to the
  measured 0.54-0.56 and not the 1/1.5 = 0.67 of the mesenchyme schedule alone. The plotted simulated
  ratio is therefore the relaxed composite's, so it does measure the same thing as the experiment, and
  it matches it to within about 0.05.
- **q_figS7_panel**: the endoderm circumference Se is plotted in Fig. 4B (top left), as the audit
  supposed. It is read as `f4b_circ_endo_meas`.

## Left out

- **Fig. 1 (p. 1)**: micrographs and a schematic; no values.
- **Fig. 2A, 2C, 2D (sections and schematic), 2E, 2F**: micrographs and drawings.
- **Fig. 3A (left schematic), 3B, 3C and 3D (photos and sections)**: micrographs and drawings.
- **Fig. 4A, 4C**: model drawing and simulation renderings; no axes.
- **Fig. 5**: sections, clay models and simulation renderings.
- **Fig. 6A, 6B, 6D, 6E**: sections and renderings. The colour bar of 6D (0.1-0.3, distance to the
  centre line) belongs to renderings with no extractable values.
- **Figs. S1, S2 (p. 17)**: stained sections and luminal photographs; no plotted values.
- **Fig. S3 A-G (p. 18)**: photographs and finite-element meshes.
- **Fig. S3 H-J (p. 18)**: the force-displacement points and fits behind the moduli. Not read because
  the panels are a blurred low-resolution raster where the open markers merge with their own connecting
  lines and with the overlapping 'Numerics' curves. Hole detection and ring-template matching both
  missed most points and found spurious ones (q_s3_force_curves_unread).
- **Figs. S4, S5 (p. 19)**: drawings of cut tubes. The opening angles are printed in the caption.
- **Fig. S6(a), the eight opening-angle curves**: drawn in similar colours on top of each other below
  about 140 µm, so they cannot be told apart.
- **Figs. S7-S11 (pp. 21-25)**: a segmentation example, proliferation images, simulation renderings, a
  growth map and species photographs; no axes with values.
