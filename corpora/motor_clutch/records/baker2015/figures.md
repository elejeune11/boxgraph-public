# Figures in baker2015

Figure pass of 2026-11-21. All readings are `mode: code`, rendered at 1200 dpi, and each was run with
`boxgraph figure check` and its overlay inspected (`figwork/<reading id>.png`, not committed). Shared code:
`figures/_kit.py` (axes from tick marks, bars with their error-bar caps, outlined white bars, box plots,
outlined histograms, marker blobs), with panel readers `_fig2c.py`, `_fig3.py`, `_fig5k.py`, `_s2e.py`,
`_s2k.py`, `_s6b.py`, `_hist.py` (`_load.py` is unused). Misfit is the largest residual of the axis fit, in
pixels at 1200 dpi. In every bar chart of this paper the error bars are drawn upward only, so each lower end is
taken as the mirror of the upper (the readings say so). Categorical bars are indexed 1, 2, ... left to right
(`condition_index`), as named in each reading's `what`.

## Read

- **Fig. 1c** (p. 2, single-fibre modulus): `fig1c`, four black bars at the doses printed under them (1,000-
  50,000 mJ cm-2, used as x), y on ticks 0-15 GPa (misfit 0.3 px). `fig1c_1000`, `fig1c_50000` are the end bars,
  compared with the text's range: 10 GPa reproduced; the lowest bar is about 0.40 GPa, not 140 MPa
  (q_fig1c_range_min).
- **Fig. 1d** (network modulus): `fig1d`, four bars at 0-18,000 mJ cm-2 (misfit 0.2 px). `fig1d_0_6000` against
  the Fig. 3 caption's 2.8 and 55 kPa: 55 reproduced; the 0 mJ bar is 5 px tall and differs from 2.8 kPa by less
  than a pixel (q_small_bar_resolution).
- **Fig. 1e** (hydrogel modulus): `fig1e`, four bars at 1,000-18,000 mJ cm-2 (misfit 0.3 px); the caps of the two
  short bars lie on the bar tops and are read as the middle of the cap stroke. `fig1e_1000`, `fig1e_18000` against
  450 Pa and 45 kPa (45 reproduced; 450 Pa within a pixel, q_small_bar_resolution). `fig1e_3000` (22.9 kPa) against
  the stiff gel's 19.1 kPa: not reproduced. This bears on q_gel_stiff_dose (q_fig1e_stiff_gel).
- **Fig. 2c** (p. 3, construct contraction against day): `fig2c_fibre_0`, `_50`, `_500`, `_6000` (fibre
  networks), `fig2c_col_2`, `_6` (collagen), `fig2c_gel_750`, `_3000` (hydrogels): the marker centres of each
  series, by colour. The x axis is calibrated on the day ticks and the y axis on the 25-100 ticks; the day-0 x tick
  and the 0 y tick of the fibre panel are covered by markers and error bars, so they are extrapolated (misfit
  0.0-0.4 px). Markers hidden under another series' marker are not read: day 0 of every series but the top one
  (all are 0 by construction), and days 0, 1, 3 of the 3,000 mJ hydrogel (under the 750 mJ markers). A marker
  partly hidden widens its interval by the hidden part. **Error bars not read**: in the fibre and hydrogel panels
  the bars of four (two) series overlap one another and lie on the axis and frame lines at days 0 and 3, and each
  series' bar is drawn in its own colour over the others, so their ends cannot be assigned to a series.
- **Fig. 3b** (p. 4, cell area): `fig3b_gel`, `fig3b_fibre`, `fig3b_collagen`, two bars each (grey soft or
  0.5 mg/ml, black stiff or 7.0 mg/ml), with s.d. bars (misfit 0.2-0.3 px).
- **Fig. 3d** (proliferation): `fig3d_gel`, `fig3d_fibre`, `fig3d_collagen` likewise. `fig3d_fibre` gives the
  soft/stiff ratio 3.30 (`soft_stiff_ratio`), against the text's "threefold": reproduced (`cmp_prolif_ratio`).
- **Fig. 5c-f** (p. 6, cell area, total FA area, FA number, average FA size; what cao2017 compares with): `fig5c`,
  `fig5d`, `fig5e`, `fig5f`, four bars each (hydrogel soft, stiff; fibres soft, stiff), with s.d. bars (misfit
  0.0-0.3 px).
- **Fig. 5h** (pFAK at FAs): `fig5h`, two bars (misfit 0.3 px).
- **Fig. 5i, 5l** (proliferation): `fig5i`, `fig5l`, three bars each, the third a white bar drawn as an outline
  (read from the centre of its top stroke).
- **Fig. 5k** (fibre recruitment, box plots): `fig5k_median` (median line of each box, with the whisker ends as
  its bar, `error_bars: unstated` since the caption does not define boxes or whiskers), `fig5k_q1`, `fig5k_q3`
  (lower and upper box edges). Each box is the largest connected stroke of its grey level over its x tick
  (misfit 0.0 px).
- **Supp. Fig. 2e** (p. 12, example fibre deflection-indentation curves; a blurred embedded bitmap):
  `figs2e_500` (green, at 100-500 nm) and `figs2e_9000` (red, at 30-75 nm). y on the frame and dashed gridlines
  (misfit 2.0 px), x on the centres of the printed labels (misfit 3.4 px); the steep red line's interval carries its
  slope times the x misfit. The blue 36,000 mJ/cm2 curve is left out: it is nearly vertical (depth 10-25 nm), so
  a force at a given depth cannot be read from it.
- **Supp. Fig. 2k** (network force against depth; blurred bitmap): `figs2k_18000`, `figs2k_6000`, `figs2k_2000`,
  `figs2k_0`, `figs2k_0weld`, every visible marker of each colour as a point (depth, force); the legend box is
  found and ignored. y on the frame and dashed gridlines (misfit 1.2 px), x on the label centres (misfit 2.0 px;
  the frame lines agree with "0" and "200" within 3.5 px). Points at the origin, and the 0 mJ points at 25 and
  50 um, are hidden under other markers. `membrane_indentation` is run on the 0 mJ and 6,000 mJ depths with the
  printed 2.8 and 55 kPa: not reproduced by a factor of 20-300, and cubic where the data are about linear
  (q_membrane_s2k). This settles the check asked for in q_membrane_inputs_plotted and q_membrane_magnitude.
- **Supp. Fig. 3c** (p. 13, FITC fluorescence): `figs3c_soft` (black), `figs3c_stiff` (grey), four bars each at
  the FITC-RGD concentrations printed under them (misfit 2.0 px; a blurred bitmap).
- **Supp. Fig. 4** (p. 14, cell area against RGD): `figs4`, five outlined grey bars at 0-6.0 mM (misfit 2.2 px);
  error bars `unstated` (the caption does not say).
- **Supp. Fig. 6b** (p. 16, bead displacement against distance): `figs6b_gel`, `figs6b_fibre`. Only markers the
  size and shape of one whole marker are read (all three cells together; each point's note names the cell's
  colour): 48 of the hydrogel beads and 64 of the fibre beads. Markers merged with others into clusters are left
  out, so each reading is a subset of the plotted beads, not all of them; a marker partly covered widens its
  interval by the lost part.
- **Supp. Fig. 7** (p. 17, fibre-diameter histograms): `figs7_06`, `figs7_05`, `figs7_04`, `figs7_03`, bin by bin
  (bin centre as x). A bin is the space between two dark side strokes standing on the axis; its top is the dark
  top stroke, found under the fitted Gaussian where the curve crosses it (wider intervals there). The four
  histograms sum to 99-100%. Their moments (`histogram_moments`, reconstructed) against the printed mean ± s.d.:
  all four means and three s.d.s reproduced; the 0.6 mg/ml s.d. is 0.53 against 0.55 µm, within what binning
  changes. The overlay panel repeats these histograms and is not read again.
- **Supp. Fig. 8a** (p. 18, cell death): `figs8a`, two bars; error bars `unstated`.
- **Supp. Fig. 9** (fibre diameters, soft and stiff): `figs9_soft`, `figs9_stiff`, bin by bin as Supp. Fig. 7
  (sums 99.7%). Moments against the printed 1.95 ± 0.37 and 1.97 ± 0.42 µm: reproduced or close. The overlay panel
  repeats them and is not read again.
- **Supp. Fig. 10a** (p. 19, proliferation against fibre density): `figs10a_soft`, `figs10a_stiff`, three bars
  each (grey error bars, read with a lighter ink threshold).

## Left out

- **Fig. 1a, 1b; Fig. 2a, 2b; Fig. 3a, 3c; Fig. 4a-c; Fig. 5a, 5b, 5g, 5j; the micrographs of 5k; Supp. Figs
  2a-d, 2f-j, 3a-b, 5, 6a, 8b, 10b, 11**: drawings, photographs and micrographs, no values to read.
- **Fig. 4d** (FITC-RGD density against time): ten single-cell traces per panel drawn in one colour, crossing
  one another (soft) or lying on top of one another (stiff); single trajectories that cannot be told apart. The
  text's "2-3-fold" (rgd_fold_soft) therefore stays without a figure check.
- **Supp. Fig. 6c**: displacement of five representative single beads against time, single trajectories.
- **Supp. Fig. 1** (NMR spectrum): no calibrated intensity axis; its values are the printed peak positions and
  integrals, which no quantity of this record uses.
- **The overlay panels of Supp. Figs 7 and 9**: the same histograms as the single panels, drawn again.
