# Figures in chaudhuri2015

All readings are `mode: code`. Every reading was run with `boxgraph figure check` and its overlay
inspected (`figwork/<reading id>.png`). The second pass reads with the shared kit
`figures/_kit.py` (axes from tick marks or, where a panel has none, from the centres of the
printed labels; lines traced by colour from a seed; bars with their error-bar caps; markers by
colour with hole filling and opening), plus panel readers `_fig2b.py`, `_figs3b.py`, `_figs5.py`.
Misfit is the largest residual of the axis fit, in pixels at the reading's dpi (1200 unless noted).

## Read

- **Fig. 1b** (p. 3, lattice model, elastic): `fig1b_400_fig`, `fig1b_225_fig`, `fig1b_56_fig`,
  `fig1b_6_fig`, the four red-to-orange lines at 10 stiffnesses (0.01-10 pN/nm). The panel has no tick marks.
  x is calibrated on the centres of the labels 0.01-10 (misfit 31 px: the label "1" is about 0.05
  decade off, q_fig1_xlabels). y is calibrated on the labels "0" and "5.0", with the 18 px offset between the
  labels and the drawn axis lines carried. Values are returned in nm^2, from the axis label x 10^4.
  The 56 lig line lies on the axis at 0.01 and is read from 0.02.
- **Fig. 1c** (p. 3, stress relaxing): `fig1c_400_fig` … `fig1c_6_fig`, five green lines. The y labels
  0, 0.5, 1.5, 2.0 and 3.5 are not evenly spaced (q_fig1c_ylabels), so a straight line is fitted
  through all five and its misfit (61 px, about 0.15 x 10^4 nm^2) is carried. The x misfit is 2 px.
  Above about 1 pN/nm the 400 and 225 lines coincide.
- **Fig. 1d** (p. 3, stress relaxing − elastic): `fig1d_400_fig` … `fig1d_6_fig`, five grey lines,
  identified by grey level (darkest to lightest: 400, 225, 100, 56, 6). y is calibrated on "3.0" and "0",
  with a 24 px label-to-line offset carried. "-4.0" does not fit a linear axis through those two
  labels and is not used (q_fig1d_ylabels). The x misfit is 34 px.
- **Fig. 2a** (p. 3, measured): `fig2a_covalent_fig`, `fig2a_ionic_fig`, the grey and red stress-relaxation
  lines at 0.2-1000 s, calibrated on the log x ticks (misfit 0.1 px) and the y ticks (0.6 px). The
  covalent line is hidden under the ionic line below 0.5 s. `fig2a_ionic_s3x_fig` reads the same
  line at the x positions of `figs3a_ion_3p4_fig`, for the consistency check `cmp_fig2a_ionic_s3a`
  (q_fig2a_which_gels).
- **Fig. 2b** (p. 3, measured, mean ± s.d.): `fig2b_cov_gp_fig`, `fig2b_ion_gp_fig` (G′: filled circles and
  squares, left axis) and `fig2b_cov_gpp_fig`, `fig2b_ion_gpp_fig` (G″: open markers, right axis), 12-13
  points each with their error bars. x is read from the top frame's decade ticks (misfit 0.6 px).
  The left y axis uses its 0.6 and 0.8 ticks; the 1.0 tick is under a marker. The right axis uses its
  0.00, 0.05 and 0.10 ticks. Error bars that end inside a marker are reported as the marker's edges.
  The legend markers are excluded. The covalent G′ point at 1 Hz is hidden under the ionic marker.
- **Fig. 2c** (p. 3, measured, mean ± s.d.): `fig2c_elastic_fig`, `fig2c_relax_fig`, the grey and red bars at
  Low, Mid, High crosslinking, with error bars. The y axis is calibrated on the ticks every 2 kPa
  (misfit 0.8 px). These are checked against Supp. Table 1's AFM moduli in `cmp_fig2c_elastic_table1` and
  `cmp_fig2c_relax_table1` (new table data `supp_table1_covalent_modulus`, `supp_table1_ionic_modulus`).
- **Fig. 3b, 3c** (p. 4, measured, mean ± s.d.): `fig3b_elastic_fig`, `fig3b_relax_fig`, `fig3c_elastic_fig`,
  `fig3c_relax_fig`, three bars each, with error bars (misfit 0.2 and 0.7 px). The red bars of 3c match
  the red bars of 3b in both means and error bars, although only their first conditions are the
  same (q_fig3bc_same_bars).
- **Fig. 3e, 4a, 4d, 4e** (pp. 4-5, measured, mean ± s.d.): `fig3e_fig`, `fig4a_fig`, `fig4d_fig`,
  `fig4e_fig`, two bars each (Elastic, Stress relax), with error bars (misfit ≤ 1 px).
- **Fig. 4b** (p. 5, measured): `fig4b_fig`, the six green bars (Control … Cytochalasin), with error bars.
- **Fig. 5b** (p. 6, lattice model): `fig5b_elastic_fig`, `fig5b_e12_fig`, `fig5b_e5_13_fig`, `fig5b_e13_fig`.
  The panel has no tick marks. It is calibrated on the label centres (x misfit 2.6 px; y 0.8 px, with the
  11 px label-to-line offset carried). The Elastic line is the grey horizontal line at 20 nm.
- **Supp. Fig. 1c** (p. 8, lattice model, mean ± s.d. of 20 runs; embedded bitmap): `figs1c_fig`, 19 blue
  points. The frame's inner decade ticks 10^-4 to 10^-1 calibrate x (misfit 1.6 px) and the ticks 5 to 40
  calibrate y (3.4 px). Points closer than a marker width merge, and those blobs report their full height
  as the interval. The 'x' mark on the frame corner at (1 s, 0) is not read.
- **Supp. Fig. 1d** (p. 8): first pass, unchanged (`fig_s1d_nc5` … `fig_s1d_nc1000`): all five curves at
  12 stiffnesses. The panel is an embedded low-resolution bitmap rendered at 1000 dpi. The x axis is
  calibrated on its four evenly spaced major ticks (misfit 0.15 px), with "1" on the third tick. The
  printed end labels "10^-2" and "10^2" do not sit on ticks (q_s1d_xaxis). At 1000 dpi the minor ticks
  sit at log positions between the long ticks, which supports this calibration (q_s1d_xaxis_rerendered).
  The y axis runs from 0 at the x-axis line to 120 at the top of the y-axis line, with 10 px carried.
- **Supp. Fig. 1f** (p. 8, lattice model, bitmap): `figs1f_elastic_fig`, `figs1f_visco_fig`, the red and green
  force lines at 0.1-2 s. The calibration uses the inward ticks; the corner ticks fall on the frame and are
  not used (x misfit 1.8 px, y 3.1 px). The axis is labelled in 0.1 pN, and values are returned in pN.
- **Supp. Fig. 3a** (p. 12, measured, bitmap): `figs3a_cov_9_fig` (black, from 5 s, where it separates from the
  greys), `figs3a_ion_1p4_fig` (green, noisy; hidden at 1-2 s), `figs3a_ion_9_fig` and `figs3a_ion_3p4_fig`
  (blue, red; to 500 s). Calibrated on the ticks (0.4 px); 4 px is carried for the bitmap.
- **Supp. Fig. 3b** (p. 12, measured, bitmap): `figs3b_ion_9_fig`, the blue diamonds (G′ of the 9 kPa ionic gel),
  which are drawn on top of the other series. Calibrated on the ticks (x 2.8 px, y 2.4 px).
- **Supp. Fig. 4** (p. 13, measured, mean ± s.d., bitmap): `figs4_elastic_fig`, `figs4_relax_fig`, four bars
  each, with error bars. The stems above the bars are lighter than the outlines, so they are found with
  a separate threshold, and 4 px is carried for the bitmap.
- **Supp. Fig. 5a,b** (p. 14, measured, bitmap): `figs5a_fig`, `figs5b_fig`, six points each (Fig. 3b's
  substrates against G″ and G′/G″). Overlapping open squares in 5b are split at their horizontal edges.
  The three points crowded near x = 0 have their error bars left unreported, because the stems run into
  each other. The caption does not say what the bars are (`error_bars: unstated`).

## Left out

- Fig. 1a, Fig. 5a, Supp. Fig. 1a,b: schematics, a cartoon and a flowchart, with no values.
- Fig. 3a, 3d, Fig. 4c, Supp. Fig. 6: micrographs.
- Supp. Fig. 1e: one stochastic trajectory of a representative run.
- Supp. Fig. 2a-f (Voigt and Maxwell limits): these panels have no ticks, and their y labels are placed by the
  curves at inconsistent spacings, so no calibration is meaningful (q_figs2_left_out). Their curve labels do
  show the ligand-density mapping (q_ligand_density_from_s2).
- Supp. Fig. 3a, the covalent 1.4 and 3.4 kPa lines: in the bitmap their two greys cannot be told apart
  from each other or from the anti-aliased edge of the black 9 kPa line.
- Supp. Fig. 3b, everything except the blue diamonds: the covalent G′ triangles all lie on top of each
  other at 1.0, and all G″ symbols lie on top of each other near 0. The green and red G′ markers are
  partly covered by the blue diamonds and break into fragments. (`figures/figs3b_ion_1p4.py` and
  `figs3b_ion_3p4.py` are unused attempts.)

## What the figures say about open questions

- q_ligand_density_measures: Supp. Fig. 2's labels support "area density = line density squared"
  (q_ligand_density_from_s2).
- q_eta_names: Supp. Fig. 2's caption sides with Fig. 1's naming (q_eta_names_s2).
- q_s1d_xaxis / q_s1d_xaxis_audit: the 1000 dpi render supports the tick calibration (q_s1d_xaxis_rerendered).
- q_experimental_scope: the measured data the audit listed have now been read, except where noted above.
- Fig. 1d is not the difference of the readings of Fig. 1c and Fig. 1b on either calibration of its lower
  half (q_fig1d_ylabels). This is not checked by the build, because runs take only scalar inputs.

## Comparisons that use these readings

- `cmp_fig2c_elastic_table1`, `cmp_fig2c_relax_table1` (consistency): the Fig. 2c bars against the AFM
  moduli printed in Supp. Table 1 (low, inter., high modulus gels).
- `cmp_fig2a_ionic_s3a` (consistency): the Fig. 2a ionic line against the 3.4 kPa ionic line of Supp.
  Fig. 3a, at the same times.
- The lattice-model readings (Fig. 1b-d, 5b, Supp. Fig. 1c, 1f) have no run, because `lattice_spreading`
  cannot be run (q_lattice_unstated). The validator warns that they are never compared, and that is expected.
  The measured readings wait for a model, here or in another paper, to validate against.
