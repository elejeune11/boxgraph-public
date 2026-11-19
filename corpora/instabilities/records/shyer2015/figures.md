# Figures of shyer2015

Every plot in the paper is a small embedded raster of about 300 dpi. Each is rendered at 1200 dpi (each
source pixel a 4 x 4 block; more dpi adds nothing) and read by code in `figures/`. The bar charts share
`figures/_xlbars.py`: it calibrates y on the axis's own tick marks fitted to the printed labels, takes each
bar's value at its top edge, and reads the SD error bar caps. A lower cap hidden in a black bar is taken as
the mirror of the upper cap, and the reading's note says so. No model in the corpus predicts any of these
measurements, so there are no runs or comparisons. They are recorded as `measured` data for later papers'
models.

- **Fig. 1, 3, 4A, 4B, 4D, 6A, 6C, 7, S2, S4, S5**: micrographs, in situ hybridizations and schematics.
  Left out: there are no values to read.
- **Fig. 5A-C, S1**: luminal views, the diffusion schematic ("Model") and drawings. Left out: there are no
  values to read.
- **Fig. S3**: simulated concentration shown as colour maps in arbitrary units (scale 0-3) on unspecified
  geometries. Left out: there is no curve or point to read.
- **Fig. 2A** (p. 4, Lgr5 mRNA per unit epithelial length at E12, E15, E19). Read as `fig2a_base`,
  `fig2a_mid` and `fig2a_tip` (data `lgr5_length_*_fig2a`). The y axis is calibrated on 7 ticks (0 to 1.2),
  misfit 0.55 px. On the grey bars both SD caps are visible, and the cap midpoints fall within 2 px of the
  bar tops. On three bars the SD is too small to show a stem: E19 Mid, E19 Tip and E12 Tip. Their error bar
  is reported as at most the black dash at the bar top.
- **Fig. 4C** (p. 6, percent EdU+ cells in fold sub-regions 1-6, six treatments). Read as `fig4c_control`,
  `fig4c_cyclo`, `fig4c_shh`, `fig4c_noggin`, `fig4c_bmp4` and `fig4c_shh_noggin` (data `edu_*_fig4c`).
  Each panel is calibrated on its own six ticks (100 to 0), misfit 0.7-1.4 px. Only the Control panel prints
  labels (80, 60, 40, 20). The other five draw the same ticks at the same spacing, and they are taken to
  mean the same values (question `q_fig4c_axes`). The bars are black, so the lower SD ends are mirrored.
- **Fig. 4E** (p. 6, Lgr5 FISH molecules per unit area, base and tip). Read as `fig4e_control` and
  `fig4e_cyclo` (data `lgr5_area_*_fig4e`). The axes are pale grey, so axis ink is g < 230. Each panel is
  calibrated on its own six ticks (0.05 to 0), misfit 0.6 and 0.9 px.
- **Fig. 5D, upper graph** (p. 7, anti-SHH intensity against distance across the 100 um box). Read as
  `fig5d_e13` (blue) and `fig5d_e15` (red) at 23 distances from 2.5 to 95 um (data
  `shh_profile_e1*_fig5d`). y is calibrated on 9 ticks (one per unit, labels 8, 6, 4, 2), misfit 0.83 px.
  x has no tick marks, so it is calibrated on the centres of the printed labels 20-100. That misfit is
  12.5 px, about 0.5 um, and it widens the read window. The y axis falls at x = -0.10. The traces are noisy:
  each interval spans the lowest to the highest line pixel within ±(0.5 um + x misfit). The pale SD bands
  are not read, because they overlap each other and the other trace's band.
- **Fig. 5D, lower graph** (p. 7, E15 5 um boxes at base (yellow) and tip (pink)). Read as `fig5d_boxes`
  (datum `shh_box_e15_fig5d`) with colour masks. Both SD caps are visible, and their midpoints are within
  2 px of the bar tops. Calibrated on 4 ticks (6, 4, 2, 0), misfit 1.0 px.
- **Fig. 6B** (p. 9, control and inside-out rings). The EdU panels are `fig6b_edu_control` and
  `fig6b_edu_insideout`, with ticks 100 to 0 (labels 80-20 printed) and misfit 0.6 and 1.2 px. The Lgr5
  panels are `fig6b_lgr5_control` and `fig6b_lgr5_insideout`, with ticks 0.10 to 0 (labels 0.08-0.02
  printed) and misfit 1.0 px. On the control Lgr5 bars the caps are hardly wider than the stem, so the upper
  end is read at the stem's end. The Sox9, pSMAD and in situ panels are micrographs (left out).
- **Fig. 6D** (p. 9-10, E10 slabs, control and grid). The EdU panels are `fig6d_edu_control` and
  `fig6d_edu_grid`, with ticks 100 to 0 and misfit 1.1 and 1.3 px. In the control panel, the region-1 cap
  is near the top of the axis (about 100%). The remaining panels are micrographs (left out).

## Open questions these readings bear on

- `q_figures_unread` is settled by this pass. Every measurement plot it lists is now read, apart from the
  "Fig. 6 proliferation quantification", which is Fig. 6B and 6D and is read here.
- `q_simulation_geometry` is not settled. Fig. 5D measures a higher Shh intensity in the E15 mesenchyme
  than at E13, and a tip box about 2.6 times brighter than the base box (4.6 against 1.8). The simulation of
  Fig. S3 predicts this qualitatively, but it cannot be rerun, so the measurement cannot be compared with it.
