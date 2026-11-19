# Figures of fierling2022

One bullet per panel. Every reading is code (`figures/<id>.py`): it calibrates the axes from the
rendered crop (frame lines and tick marks matched to the printed labels, linear fit) and reports
each value with a 95% interval. Shared helpers: `_gp.py` (gnuplot frames, ticks, lines, markers),
`_fig2.py`, `_fig2a.py`, `_fig3a.py`, `_fig3b.py`, `_fig3cd.py`, `_fig4b.py`, `_fig4f.py`, `_sf1a.py`,
`_sf3c.py`, `_sf3d.py`. "Misfit" is the largest distance, in pixels at the reading's dpi, between a
calibration mark and the fitted axis. Most panels were drawn with the released gnuplot scripts
(fierling_code). Where the released files hold the plotted numbers, the readings were checked
against them; that check is stated below.

The first pass (Figs. 2c, 3a, 3b, 5d, 5e, Supp. Fig. 1f) is unchanged. The second pass (2026-11-19)
added the rest. It added one opt-in option to `_gp.read_markers` (`point: centroid`, `apex: typical`)
for gnuplot's triangle points, which none of the first pass's readings use.

## Main text

- **Fig. 1a, 1b, 1d**: micrographs and kymographs, no values. Left out.
- **Fig. 1c**: read, `fig1c_curv` (`fig1c.py`). Black mean lines and SD error bars of the ventral
  curvature at t0-t3 (x = phase index 0-3). GraphPad-style axes: outward left ticks matched to
  0.02 ... -0.08 (6 ticks, misfit 0.23 px); the categories come from the x-axis ticks. Means agree with
  the released per-embryo values (data_for_Fig_1c.tsv) to within 0.00006 1/um. The four red per-embryo
  dots per phase are not read: they overlap the bars and caps, and their values are released.
- **Fig. 1e**: drawing with the printed dimensions 180 um and 500 um (data, first pass). **Fig. 1f**:
  rendering. Left out.
- **Fig. 1g**: dotted line read, `fig1g_profile` (the pre-stress profile chosen for the simulations,
  normalised to the midline), at rows 0.5-6.5. Frame 1.2/0 and 5 ticks (misfit 0.31 px). The crop
  leaves out the time colour bar, whose frame would pass for the plot's. The measured MyoII dots
  (3 embryos, one dot per time point and row, coloured by time) are left out: in every row tens of
  dots of graded colours overlap each other and cannot be told apart. Their values are in fierling_code
  (DVbands_Area_Myo_from-19.gdat).
- **Fig. 2a**: read, `fig2a_target` (dotted steel blue, six bands), `fig2a_target_mid` (midline band),
  `fig2a_dv` (dashed navy), `fig2a_ap` (cyan). Frame and 5 ticks plus the reference line at 1 (misfit
  0.20 px). Every value agrees with the released Step013 profile to within 0.0005. The midline target
  0.7014 (band pre-strain 0.426) settles the open question q_prestress_rounding; see the new
  q_fig2a_midline_prestrain. The target is an area ratio, the actual sizes are length ratios
  (q_target_size_measure).
- **Fig. 2b, 2d, 2e, 2f**: renderings and colour key. Left out.
- **Fig. 2c**: first pass (`fig2c_prestress`, `fig2c_sap`, `fig2c_sdv`, midline band).
- **Fig. 3a**: first pass (`fig3a_area_sim`, `fig3a_area_muvi`). The confocal area line and the MyoII
  curves (right axis) are not read, as in the first pass.
- **Fig. 3b**: first pass (`fig3b_sim`, `fig3b_sim_r7`, `fig3b_muvi`, `fig3b_confocal`).
- **Fig. 3c**: read, `fig3c_muvi` (goldenrod up-triangles with min-max bars), `fig3c_confocal` (red
  up-triangles), `fig3c_sim` and `fig3c_sim_c` (cyan line at the measured rows). y from the frame, the
  ticks and the reference line at 1 (misfit 0.20 px); x from the 9 row ticks (0.33 px). The triangles'
  point is their centroid (gnuplot); the apex height comes from the median height-to-width ratio.
  Checked against the released data: MuVi means (rauzi_t=-1_cell_AP_width_over_time.gdat) and confocal
  means (From_-19_t=-13.0.gdat) fall inside every interval. The simulated line matches Step037 column 12.
  Not read: MuVi rows 3 and 6 (the red triangle covers the flat side) and confocal rows 1, 5 and 6
  (the cyan line covers the flat side).
- **Fig. 3d**: read, `fig3d_muvi`, `fig3d_confocal` (down-triangles with dashed bars), `fig3d_sim`,
  `fig3d_sim_r7` (dashed navy line). Calibrated as 3c (misfit 0.21 px). The released means match to
  within 0.002. MuVi row 6 is not read (the confocal triangle covers it). See q_rows_ap_dv.
- **Fig. 3e, 3f**: renderings of stripes. Left out.
- **Fig. 4a, 4d, 4e**: rendering and micrographs. Left out.
- **Fig. 4b**: simulated dashed lines read at x = 0, 50, 100, 150 (`fig4b_sim0` ... `fig4b_sim150`),
  before furrowing (t = -3 to 2 min). y uses the right-frame ticks (the lines drawn over the left ticks
  at 20 and 0 hide them; misfit 0.40 px). Each dashed line is searched in a band of values that leaves
  out the solid and dotted lines of the same colour. Not read: the x = 200 dashed line, which touches
  the solid x = 200 line of the same red at every time; the dashed lines after 2 min, where they meet
  the solid ones; the blue slope arrows. The measured solid (posterior) and dotted (anterior) lines are
  the means of Supp. Fig. 3d, read there. The simulation is compared with those readings at the same
  times (cmp_furrow_z_*); see q_furrow_z_offset.
- **Fig. 4c**: simulation read, `fig4c_sim` (blue open squares). Outward x ticks below the frame
  (5 ticks, misfit 0.40 px). The bottom frame line, cut by markers drawn over it, is found where the
  left frame line ends. Six of nine squares are read: the squares at 0, 63 and 108 um have goldenrod
  markers or lines drawn over their sides. The six agree with the released rate_of_furrowing_t=3.gdat
  to within 0.0013 um/min. The six MuVi embryos (filled markers of six shapes, one colour, joined by
  lines) are left out: up to six markers overlap at each position, five or six of them on zero. Their
  values are in rate_of_furrowing_t=3.gdat.
- **Fig. 4f**: read, `fig4f_ap_muvi`, `fig4f_ap_sim`, `fig4f_dv_muvi` (with its min-max band),
  `fig4f_dv_sim`, at t = -4 ... 4 min. y from 6 ticks and the zero axis (misfit 0.50 px). The
  semi-transparent band is drawn over some frame ticks: those dark tick pixels are restored before
  calibrating. Where the band lies over the DV simulation line, the line is searched in the band-tinted
  colour too. The measured curvature files are not in the release (local paths), so these readings
  are the only record of them. The AP band is too thin to read.
- **Fig. 5a, 5b, 5c**: renderings and micrographs. Left out.
- **Fig. 5d, 5e**: first pass (`fig5d_stress`, `fig5e_recoil_pos`, `fig5e_recoil_neg`).

## Supplementary Figures

- **Supp. Fig. 1a**: main panel read, `sf1a_sap` (green sigma_AP) and `sf1a_sdv` (purple sigma_DV) at
  pre-stress 250-1250. Frame 3000/0 and 5 ticks (misfit 0.41 px). The rows searched stay below the
  inset. The inset (pre-stress 0-200) is left out. It magnifies the same two simulated curves, and
  their values at the two marked pre-strains are read more precisely, band by band, in Fig. 2c and
  Supp. Fig. 1f.
- **Supp. Fig. 1b, 1d**: renderings. **Supp. Fig. 1c**: drawing with printed strains (data, first
  pass). Left out.
- **Supp. Fig. 1e**: read, `sf1e_target_mid`, `sf1e_dv`, `sf1e_ap`, in the first bands (width pi/80).
  Frame, 8 ticks and the reference line (misfit 0.49 px). These agree with the released Step063 file
  to within 0.0002.
- **Supp. Fig. 1f**: first pass (`sf1f_prestress`).
- **Supp. Fig. 2a** (area, AP and DV size by row over time, confocal dashed lines for 7 rows with
  shaded min-max bands, and simulation dots coloured by row) and **Supp. Fig. 2b** (area over time
  for 10 MuVi rows and 7 confocal rows): left out. Each panel crosses 7-17 lines in seven to ten
  colours with overlapping translucent bands, and the simulation dots of the same colours lie on the
  lines, about one inch tall at print size; the rows cannot be told apart. Their t = -1 min values
  are read in Figs. 3b-3d. The full series are in fierling_code (Guy_area_myo.gdat,
  sync_rauzi_area.gdat, cell_*_width_over_time_*.gdat, sims_t=*_area.gdat).
- **Supp. Fig. 2c-2g**: rendering and kymographs. Left out (the printed distances in 2e and 2g are
  labels on kymographs, not plotted data).
- **Supp. Fig. 3a, 3b**: rendering and micrographs. Left out.
- **Supp. Fig. 3c**: read, `sf3c_{ant,mid,post}_{ap,area}` (AP size solid, area dashed, one colour per
  bin) at t = 1-5 min. From 1 min on, the two lines of each colour separate: the upper run is the AP
  size, the lower the area. y from 6 ticks and the bottom frame (misfit 0.36 px). Not read: before
  1 min, where the six lines and their hatched bands cross, and two dash gaps (anterior area at
  3 min, posterior area at 4 min).
- **Supp. Fig. 3d**: read, `sf3d_m150` ... `sf3d_p200` (eight planes, t = -3 to 8 min) and
  `sf3d_p0_e` ... `sf3d_p150_e` (the times of Fig. 4b). Frame 60/0 and 5 ticks (misfit 0.32 px),
  after restoring the tick pixels darkened by the bands drawn over them. The light-blue and yellow
  lines are searched with a tight colour tolerance, because overlapping bands make colours close to
  theirs. All agree with the released depth_along_AP.gdat, whose plotted column is the mean, not the
  median the caption names (q_sf3d_mean_median). The bands are not read: up to five overlap. After
  8 min the lines meet and are not read.
- **Supp. Fig. 3e**: left out. The six per-embryo DV curvature curves are drawn in six orange tints
  about 30 RGB units apart with different dash patterns; they cross repeatedly and cannot be followed.
  Their mean and min-max are read in Fig. 4f. The simulation line repeats Fig. 4f's.
- **Supp. Fig. 3f**: read, `sf3f_depth` (simulated furrow depth against myosin pre-stress) at 3000-7000.
  Frame and 7 ticks (misfit 0.27 px). Below 3000 the line lies on zero. The y label's "um" is
  questioned in q_sf3f_depth_unit.
- **Supp. Fig. 3g**: read, `sf3g_pole` (mean and SD of the anterior pole's inward movement, n = 5).
  Outward ticks 8 ... 0 (misfit below 0.1 px). The mean 3.54 um equals the mean of the five dots as
  plotted. The micrographs are left out.

## What the figures settle

- q_prestress_rounding: the plotted midline pre-strain is the first band's mean, 0.426 (Fig. 2a target
  0.7014; released 0.70138), not 0.43 (q_fig2a_midline_prestrain).
- The "target size" of the strain profiles is an area ratio plotted beside length ratios
  (q_target_size_measure); the model target_size reproduces it from the stated pre-strain.
- Supp. Fig. 3d's lines are means, against its caption (q_sf3d_mean_median).
