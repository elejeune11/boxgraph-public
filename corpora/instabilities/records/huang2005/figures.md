# Figures of huang2005

Figure pass, 2026-11-13. Every plot with values is read by code (`mode: code`), rendered from the
vector PDF at 900 dpi (Figs. 3, 7, 10, 11) or 1200 dpi (Fig. 5). All readings share
`figures/_common.py`; each `figures/<reading id>.py` only sets the axis labels, colour, seed and
filters. How the shared code works:

- **Calibration.** The y axis is the longest vertical black run in the left half, the x axis the
  longest horizontal run in the lower half. The labelled ticks are the longest ticks that stick out
  from the axis (left of y, below x). The evenly spaced ones are kept and matched in order to the
  printed labels, and a straight line is fitted (in log10 on the log axes of Figs. 3 and 5). The
  misfit is the largest residual, taken as at least 0.5 px. It was 0.0-0.8 px on every panel; at
  these dpi that is below 0.1% of a decade.
- **Curves** are colour masks inside the frame (red, blue, green, or black for black lines), traced
  column by column from a seed. A value is the centre of the line. Its 95% interval is the ink
  extent within the x misfit, widened by the y misfit. A line partly hidden under another gets an
  interval that spans the whole stack of ink in that column. A position is left out of `at` when
  there is no clean run there: the curve is hidden under another, crosses a label, or merges with
  the other curves.
- **Markers** (Figs. 7, 10, 11): their holes are filled, the lines are opened away, and each marker
  is read at the centre of its bounding box. The interval is the misfit plus 2 px plus the
  centroid offset (for triangles). Shapes are told apart by box size and fill ratio: stars about
  18-25 px wide and at most 21 px high; circles 26-31 px high with fill at least 0.70; triangles at
  most 26 px high with fill below 0.70. Symbols that overlap one another are merged blobs, and they
  are not read.

Panels:

- **Fig. 1, 2 (pp. 2-4), Fig. 4 (p. 6)**: schematics and sketches of the energy. Nothing to read.
- **Fig. 3 (p. 6)**: g against kH, four curves. They are read as `fig3_nu0` (green), `fig3_nu04`
  (blue), `fig3_nu049` (red) and `fig3_nu05` (thin black), at kH = 0.012-7. The blue curve is not
  read at kH = 5 and 7, nor the red at 7, because the green curve covers them. The black curve is
  read only up to kH = 1.2, where it runs into the red. The dashed g = 1/2 line is the thick limit,
  already compared as printed (g_thick_fig3), so it is not read. Runs: `g_eq10`, swept over kH.
- **Fig. 5 (p. 9)**: six panels, each with blue, red and black curves (Ē/Ē_s = 10^3, 10^4, 10^5).
  The readings are `fig5{a..f}_{1e3,1e4,1e5}`: a/b are N_c/(Ē h) for nu_s = 0.4/0.5, c/d are
  lambda_eq/h, and e/f are the normalized amplitude. All are read at H/h = 0.15-700. The dashed
  slope triangles and asymptotes are removed by an opening of radius 2 px. In panels e and f the
  three curves lie on top of one another at the 0.815 and 1.0 plateaus, so the hidden ones are not
  read there. The middle panels have only two labelled y ticks (10, 100), so their calibration is
  exact by construction (misfit 0.5 px assumed). The 1200 dpi render shows overbars on the labels
  (Ē/Ē_s) and on the ordinate N_c/(Ē h). This settles q_fig5_modulus_ratio in favour of the
  plane-strain ratio, as the audit's q_fig5_labels_overbar suggested. The new inputs `Ebar_fig5_*`
  are therefore plane_strain_modulus_ratio. Runs: `sinusoidal_finite_substrate`, swept over H/h.
  The power-law slopes marked by the triangles (1/2, 1/4, 1, 1/2) are drawn guides, not read.
- **Fig. 6, 8, 9 (pp. 11, 13, 14)**: grey-scale simulated patterns with Fourier insets. There are
  no values to read.
- **Fig. 7 (p. 12)**: `fig7_stripes` is the black analytical line, read at |N|/N_c = 1.5-10.5 and
  compared with `rms_stripes`. `fig7_labyrinth` is the red squares, five simulated labyrinth
  points. The legend square is dropped because legend text stands beside it. The first square
  (x ≈ 1.02) is crossed by the black line, which a closing bridges. These squares are outputs of
  the spectral simulation, which is not run here (q_kbar_not_rerun), so they are recorded
  uncompared. The paper says they lie above the stripe line, so comparing them with `rms_stripes`
  would only restate that.
- **Fig. 10 (p. 16) and Fig. 11 (p. 17)**: two panels each, A/h (a) and lambda_eq/h (b) against
  |N011|/N_c, for Ē/Ē_s = 1000 and H/h = 1, 10, 100.
  - **Lines.** `fig1{0,1}{a,b}_line_H{1,10,100}` are the solid analytical lines. They are read at the
    half-integers 1.5-19.5, between the symbols, with the symbol areas kept from steering the trace.
    Fig. 10a is not read at 1.5, where the three lines meet. Runs: the new model `postbuckling_eq16`
    (Eq. 16 through `sinusoidal_finite_substrate`), swept over |N|/N_c; comparisons are reproduction.
  - **Symbols.** `fig1{0,1}{a,b}_sym_H{1,10,100}` are the stars, circles and triangles of the
    Appendix numerical solution with interface shear. They are compared with the same model as
    `approximation`, which tests the paper's claim that shear can be neglected. Fig. 10b has circles
    only at 1-12, 14, 16 and 18, as drawn. Circles and triangles that overlap in Fig. 10a (x ≤ 9)
    are not read.
  - **What the symbols show.** In Fig. 11b the symbols lie well below the lines: about 9.8 against
    11.8 for H/h = 1, and 28.8 against 30.1 for H/h = 10. In Fig. 11a the symbols for H/h = 1 and
    10 also fall below the lines at large force. The paper does not comment on this; see
    q_fig11_shear_difference.
