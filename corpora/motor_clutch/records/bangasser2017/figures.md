# Figures of bangasser2017

Figure pass of 2026-11-19. The first pass read no figure (its tools were refused; q_eye_only_figures).
Every plot with values is now read by the record's own code: `figures/<reading id>.py`, each a stub
that calls the shared reader `figures/_kit.py` (method in its docstring) and pins its SHA-256.

**How the readings are made.** The article figures are vector graphics, rendered at 1600 dpi (Figs.
1c-f, 2, 3, 4a-e) or 1200 dpi (Figs. 1g, 4f); the Supplementary figures are raster Excel charts,
rendered at 900 dpi. Each axis is calibrated from the image: the axis line is the longest straight run
of the axis colour (red, blue or gold for the two-axis panels 1d, 3f, 4b), its tick marks are the short
runs of one common length leaving it, and they are matched in order to the printed labels (a tick
hidden under a marker is placed on the evenly spaced label grid; a 0 tick hidden in the corner is the
x axis line). The largest calibration misfit is printed in every value's note: 0-1.5 px for the
article panels, up to about 3.6 px for the raster panels. Markers are located by their fill colour
(by hue for the shaded raster markers): the centre is every point where the visible fill fits a disc
of the series' radius inside the ink, and the value's interval is that set's extent plus the misfit.
A marker hidden under another series' marker gets the wider interval of the ink that hides it, and its
error bar is not read. Error bars are the black stems at the marker's column, ended by their caps; a
bar that never leaves its marker is reported as at most the marker (Figs. 1c, 1d and most of 1e-f,
where the s.e.m. is smaller than the marker); a stem that runs into other ink without a cap is taken
as the mirror of the other end. Bar charts: each bar's top outline stroke and its error bar. Curves
(Supplementary Figs. 2E, 5A-D): traced column by column in the series colour; at a sampled time the
run in that column is the plotted s.e.m. bar, whose middle is the mean.

Every reading was checked with `boxgraph figure check` and its overlay (`figwork/<id>.png`): the
magenta marks sit on the markers, bars or traces meant. x positions of the measured points are the
moduli of Supplementary Fig. 1A (50 Pa, 740 Pa, 4.6, 9.3, 19.8, 98.5, 195 kPa), which the markers'
read-back x confirm (in each note); x of the ECFN series (data of Chan and Odde 2008) and of
Supplementary Fig. 5E-H is read from the image.

## Fig. 1 (p. 3), simulated, low (red) and high (blue) motor-clutch sets; s.e.m.

- **1a, 1b**: left out, a schematic and a schematic over a phase image.
- **1c** actin flow: `fig1c_low`, `fig1c_high` at 0.01-1000 pN/nm (log x; labels 0.01, 1, 100). y misfit
  1.5 px. The blue markers at 1, 100 and 1000 pN/nm are hidden under the red ones: wider intervals, no bars.
- **1d** traction force, two y axes: `fig1d_low` on the red left axis (0-800 pN; the 400 tick is hidden by
  a marker and placed on the grid), `fig1d_high` on the blue right axis (0-6,000 pN). Both series peak at
  0.1 pN/nm (q_figures_settle).
- **1e** aspect ratio: `fig1e_low`, `fig1e_high` (one tick hidden, placed on the grid).
- **1f** random motility coefficient: `fig1f_low`, `fig1f_high`. The red series peaks at 1 pN/nm and the
  blue at 10 pN/nm, which settles q_fig1f_swapped (see q_figures_settle).
- **1g** composite metric: `fig1g_low`, `fig1g_high` (points with s.e.m.). Reproduced from 1c-f by
  composite_metric_sim (cmp_composite_sim_*); the printed ΔKsub,opt = 4-fold is checked from the read
  points (cmp_kfold_fig1g) and from the recomputed composite (cmp_kfold_sim) by log-Gaussian fits with
  the amplitude fixed at 1 (q_gauss_amplitude). The two fitted curves themselves are not read: the fits
  are recomputed instead.

## Fig. 2 (p. 4), measured U251; s.e.m.

- **2a, 2b**: left out, phase images and wind-rose trajectories (single trajectories).
- **2c** motility coefficient: `fig2c_u251` (7 points); `fig2c_u251_msdx` reads the same panel at the
  moduli of the MSD curves (4.6, 100, 200 kPa as the Supplementary Fig. 2 legend prints them) for
  cmp_rmc_msd. y misfit 0.7 px.
- **2d** cell area: `fig2d_u251`. **2e** aspect ratio: `fig2e_u251` (settles q_aspect_ratio_optimum in
  favour of the text; q_figures_settle). These are the untreated series of Fig. 4c-e, compared there
  (cmp_rmc_fig2c_fig4e, cmp_area_fig2d_fig4c, cmp_aspect_fig2e_fig4d).

## Fig. 3 (p. 5), measured; s.e.m.

- **3a, 3b, 3d**: left out, a fluorescence image, a kymograph and traction-field images.
- **3c** actin flow: `fig3c_u251` (blue, 0.74-195 kPa), `fig3c_ecfn` (gold, ECFN from ref. 7, x read
  from the image); the legend key inside the plot is masked out. cmp_flow_fig3c_fig4a against Fig. 4a.
- **3e** strain energy on 700 Pa, log axis: `fig3e_bars` (bar 1 ECFN, bar 2 U251). The text's "~400
  times" is their ratio; no model in the record computes it, so it is recorded without a verdict.
- **3f** strain energy, two axes: `fig3f_ecfn` (gold left axis, pJ), `fig3f_u251` (blue right axis,
  unlabelled; pJ from Fig. 3e: q_fig3f_right_axis). cmp_strain_fig3f_fig4b against Fig. 4b.

## Fig. 4 (p. 6), measured U251, untreated (blue) and with blebbistatin + cyclo(RGDfV) (red); s.e.m.

- **4a-e scatter panels**: `fig4a_nodrug/_drugs` (flow), `fig4b_nodrug` (blue right axis) and
  `fig4b_drugs` (red left axis; the red marker at 19.8 kPa is hidden under the blue one), `fig4c_*`
  (area), `fig4d_*` (aspect ratio; four blue markers partly hidden under red ones), `fig4e_*` (motility).
  Where two series' error bars overlap, a stem that meets the other series' cap is taken as the mirror
  of its own other end (stated in the value's note). These feed composite_metric_exp
  (cmp_composite_exp_*) and the ΔEopt = 2-fold check (cmp_Efold_*).
- **4a-e bar insets** (10 charts, bars left to right No drug, Blebbistatin, cyclo(RGDfV), Both drugs):
  `fig4a_bars_4kPa`, `fig4a_bars_100kPa`, `fig4b_bars_4kPa`, `fig4b_bars_9kPa`, `fig4c_bars_4kPa`,
  `fig4c_bars_100kPa`, `fig4d_bars_4kPa`, `fig4d_bars_100kPa`, `fig4e_bars_4kPa`, `fig4e_bars_100kPa`.
  The hatched bars' outlines are found as for solid bars (one hatched edge broken by the hatching is
  placed at the bar width). Their categorical x axis has no moduli, so they are not compared with the
  scatter panels; they bear on q_fig4b_traction_drop (q_figures_settle).
- **4f** composite metric: `fig4f_nodrug`, `fig4f_drugs` (7 points each; markers sitting on the x axis
  read with wide intervals), `fig4f_ecfn` (gold; four of the six ECFN points: the two markers at about
  0.3 and 1.1 kPa lie on the thick gold fit curve and cannot be separated from it by colour). The
  three fitted Gaussian curves are not read; their optima are refitted (cmp_Efold_fig4f, cmp_Eopt_fig4f_*).
- **4g**: left out, an illustration.

## Supplementary figures (raster)

- **Supp. 1A** (p. 15): a recipe table with the measured moduli, used above as the x positions of the
  measured points; **1B-D**: left out, a schematic and images.
- **Supp. 2A-D** (p. 16): left out, images and trajectories. **2E** averaged MSD: `figs2e_msd_4kPa`,
  `figs2e_msd_100kPa`, `figs2e_msd_200kPa`, read every 15 min at the bars (q_rmc_msd; the key prints
  "4 kPa", q_supp2e_key). y misfit 3.6 px. Eq. 12 on these: cmp_rmc_msd.
- **Supp. 3** (p. 17): left out. 3A is a heat map of fold changes (colour classes, not a plot of values);
  3B is a histogram of some thousands of one-count bins, narrower than a pixel of the page raster, and
  feeds nothing in this record.
- **Supp. 4** (p. 19, legend p. 20): **4A, 4B** left out (kymographs). **4C** `figs4c_bars`. **4D**
  `figs4d_ecfn`; **4E** `figs4e_u251`; **4F** `figs4f_bars`; **4G** `figs4g_ecfn`; **4H** `figs4h_drugs`;
  **4I** `figs4i_u251`. The grey "noise" points of 4D and 4E are left out: their grey fill cannot be
  told by colour from the grey antialiasing of the black ink at this raster resolution. The x axes of
  4D and 4G-I print "Pa" (kept as printed; q_supp4_pa_axis); 4D and 4G place the second ECFN point
  differently (q_supp4d_ecfn_x).
- **Supp. 5** (p. 21): **5A** `figs5a_0p1`, `figs5a_1000`, `figs5a_10`; **5B** `figs5b_0p1`,
  `figs5b_1000`, `figs5b_10` (traces read at 25-195 min). **5C, 5D**: only the gold 0.1 pN/nm traces
  (`figs5c_0p1`, `figs5d_0p1`); the red and blue traces cross each other at every step (noisy and
  overlapping), so they cannot be followed apart. **5E-H** `figs5e_nc`, `figs5f_nc`, `figs5g_nc`,
  `figs5h_nc` (green points, x read from the image; in 5E the point at Nc = 1,250 sits on the x axis and
  is not found). The simulator is not run in this record (q_cms_not_run), so these are recorded
  without a run.

## Results recorded without a run

The simulated curves of Figs. 1c-f and Supplementary Fig. 5 need the whole-cell simulator, which is not
run (q_cms_not_run); only the composite metric built from them, and the flow of the one-module stand-in
(cmp_module_flow_*, approximation), are compared. The measured data (Figs. 2-4, Supplementary Figs. 2E,
4) are recorded as measurements for later records to validate against; within this record they are
compared with each other where the paper plots the same data twice, and with the paper's own processing
(composite metric, Eq. 12).
