# Figures of kaneko2011

- Fig. 1, 2, 6, 8A: three-dimensional reconstructions of the capillary network; no axes or values.
  The distances in the Fig. 2 legend (about 350 um, about 130 by 120 um) are recorded from the text.
- Fig. 3 (p. 4): histogram of capillary segment lengths (20 um bins, 0-200 um). **Read**: reading
  `fig3_hist` (code `figures/fig3_hist.py`, 1200 dpi), datum `seg_len_hist_fig3`, the height of each of the
  ten bars at its bin centre. Calibrated from the image: the y axis from its eleven tick marks (0-50 in
  steps of 5, the zero tick on the x axis line; rms misfit 0.009 segments), the x axis from its eleven
  ticks (0-200 um in steps of 20; rms misfit 0.02 um). Each bar is read at the centre row of its top
  outline; 95% intervals about ±0.12-0.15 segments. Bars: 35, 39, 50, 29, 24, 18, 9, 5, 4, 3. Run
  `run_fig3_stats` (model `histogram_stats`) gives the count, binned mean and SD, compared with the printed
  n = 220 (`cmp_fig3_n`) and 61.5 ± 41.6 um (`cmp_fig3_mean`, `cmp_fig3_sd`, approximations, as the
  bin midpoints only approximate the measured lengths). The bars sum to 216, not 220: question
  `q_fig3_n_216`. This reading settles the earlier `q_fig3_not_read` (the figure is now read).
- Fig. 4: a reconstruction with the nine counting points and a printed table of the three densities;
  the table values are recorded as data (density_art, density_mid, density_ven). The drawing has a
  100 um scale bar but no values to read beyond the table.
- Fig. 5: reconstructions and micrographs of the sinuses; the volumes are in the text.
- Fig. 7, 8B-D: micrographs and schemata; no values.
