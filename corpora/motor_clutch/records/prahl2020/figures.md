# Figures of prahl2020

All figures are vector plots. Each panel was rendered at 1200 dpi (Fig. 2G) or 1500 dpi (the rest), so that
the plot box is 1100-2200 px on its shorter side, and read by code (`figures/<id>.py`, all calling the
shared `figures/_kit.py`). Calibration, the same for every panel: the axis lines are the longest runs of
black ink; the tick marks are short black runs leaving the axis lines (and the box's top and right lines
where there is a box); the evenly spaced ticks are matched to the printed labels from the low end
(`yevery: 2` where unlabelled ticks lie between labels; a log axis by its decade ticks and box corners).
The fit misfit is printed in each value's note and widens every interval; it is 0.0-1.1 px on every axis
except the x axis of Fig. 2G (1.4 px at 1200 dpi). Error bars are read end by end (cap centres) and give
each value its printed interval. Overlays: `figwork/<reading id>.png`, all checked by eye.

Earlier version of this file: no figure was read (q_figures_unread). This pass adds every reading below.

## Main text

- **Fig. 1A, 1A'** (schematics): left out, drawings with no values.
- **Fig. 1B** (individual simulated trajectories) and **Fig. 1C** (individual simulated MSD curves, no mean,
  no error bars): left out, single random trajectories in many indistinguishable colours.
- **Fig. 2A-C** (photographs, micrographs, time-lapse): left out, no values.
- **Fig. 2D** (individual cell trajectories) and **Fig. 2E** (individual MSD curves; the caption says error
  bars are not shown): left out, single trajectories.
- **Fig. 2F** (mean displacement vs time, experiment and 1D CMS): left out. Time runs down the vertical axis;
  the two series (open diamonds, filled circles, both black) and their horizontal SEM bars overlap and merge
  along the whole curve, so neither the markers nor the bars can be separated (a filled/hollow-marker
  separation on the turned image gave fragments of merged clusters, not markers). The panel legend swaps the
  symbols relative to the caption (question q_fig2f_legend).
- **Fig. 2G** (mean MSD vs time lag, SEM bars): read by colour, marker = blob after an opening wider than
  the stem, bar = the same-coloured stem's extreme rows; an end hidden by another series' ink is mirrored
  from the other end, and a lag where the marker is hidden is not read. y labels in um^2 (axis printed as
  x 10^3 um^2).
  - `fig2g_exp_fig` (black circles, n = 403 cells, measured): lags 110-170 min (below 110 the black markers
    are covered by the blue ones).
  - `fig2g_psi09_fig` (blue diamonds, psi_pol 0.9, n = 60): lags 20-80 and 110-170 min (10, 90, 100 hidden);
    `fig2g_psi09_late_fig`: the same at 110-170 min, to set beside the experiment point by point.
  - `fig2g_psi083_fig` (red squares, n = 36): 60-170 min. `fig2g_psi05_fig` (green triangles, n = 40): 10-170 min.
  - Lag 180 is not read: the points sit on the box's right line, which hides their bars.
  - Checks: Eq. 2 with the mean fitted mu, v (cmp_eq2_mean_exp, cmp_eq2_mean_sim; q_fig2g_eq2_mean) and the
    simulation against the experiment (val_fig2g_sim_exp; q_fig2g_sim_vs_exp).
- **Fig. 3A-D** (histograms of motility coefficient and velocity): `fig3a_mu_exp_hist_fig`,
  `fig3b_v_exp_hist_fig` (filled bars, n = 403), `fig3c_mu_sim_hist_fig`, `fig3d_v_sim_hist_fig` (outlined bars,
  n = 60). Bin centres are the x tick marks (2 um^2/min and 0.25 um/min apart); a bar's height is its top
  edge at the bin centre: the centre of the outline stroke for outlined bars, and for filled bars the top
  of the ink plus half an axis-line width (the edge stroke is centred on the bar top). A bin with no bar
  clear of the axis reads 0 with an interval up to two line widths. Totals: 399 (3A; three one-cell bars
  are too thin to see, q_fig3a_total), 402.6 (3B), 59.9 (3C), 60.0 (3D). Binned means against the printed
  means: cmp_mean_fig3a-d (approximation).
- **Fig. 4A-B** (simulated motility, velocity vs nclutch, log x axis): `fig4a_mu_nclutch_fig`,
  `fig4b_v_nclutch_fig` at nclutch 8, 25, 75, 250, 750. x calibrated on the decade ticks 10, 100 and the box
  corners 1, 1000. Markers: hollow diamonds (centre = the gap in the stem) / filled circles (blob centre).
- **Fig. 4C-D** (measured, vs cRGD 0, 0.1, 0.3, 1 uM): `fig4c_mu_rgd_fig`, `fig4d_v_rgd_fig`. At 1 uM in 4D
  the SEM bar is hidden inside the marker (reported as at most the marker).
  The peaks stated in the text are confirmed (q_figures_read).
- **Fig. 5A-B** (simulated vs nmotor 100, 500, 1000): `fig5a_mu_nmotor_fig`, `fig5b_v_nmotor_fig`. At
  nmotor = 100 the bars are inside the markers.
- **Fig. 5C-D, 6A-D, 7A-D** (dot plots, mean line and SEM bar per group): `fig5c_mu_y27632_fig`,
  `fig5d_v_y27632_fig`, `fig6a_mu_lata_fig`, `fig6b_v_lata_fig` (measured); `fig6c_mu_actin_sim_fig`,
  `fig6d_v_actin_sim_fig` (simulated); `fig7a_mu_mta_fig`, `fig7b_v_mta_fig` (measured);
  `fig7c_mu_knuc_sim_fig`, `fig7d_v_knuc_sim_fig` (simulated). x = condition index from the left (each
  reading's `what` names the groups); the group centres are the category ticks below the axis. The mean
  is the longest black line centred on the group (no wider than the group spacing, so p-value bars are
  excluded); the SEM bar ends are the shorter centred caps joined to it by the stem. The individual cells
  (coloured dots, 23-112 per group) are not read: they touch and overlap in the swarm, pile up along the
  axis at zero and under the mean line, so they cannot be separated or counted; each group's mean and SEM
  bar, which are read, are what the paper reports and tests.

## Supporting Material

- **Fig. S1A-C** (simulated motility, velocity, module number vs psi_pol 0.9, 0.83, 0.5): `figs1a_mu_psi_fig`,
  `figs1b_v_psi_fig`, `figs1c_modules_psi_fig`, read as the dot plots above. The psi_pol = 0.9 group equals
  the n = 60 base set (q_base_runs_shared, which bears on q_n_sims_psi).
- **Fig. S2** (confocal images): left out, no values.
- **Fig. S3A-B** (simulated, ksub 10^3 and 10^6 pN/nm): `figs3a_mu_ksub_fig`, `figs3b_v_ksub_fig`.
- **Fig. S4A** (histogram of PRW speeds): `figs4a_S_hist_fig`. The x tick marks are the 13 bin centres, not
  the labels: the labels 0 and 12 sit at the box corners, so the x axis is calibrated on the corners
  (`xcorners`) and read at the centres (k + 1/2) x 12/13. Total 402.5; binned mean 1.05 against the printed
  0.74 (q_figs4a_mean).
- **Fig. S4B** (histogram of log10 persistence time): `figs4b_logP_hist_fig`, bins 0.5 wide centred from
  -2.5 to 5.5; calibrated on the ticks -3 to 4 (the tick at 5 is hidden by the tallest bar). The grey arrow
  is not read. Total 402.2; binned mean 3.27 against the printed 3.1 +- 0.25.
- **Fig. S5A, A'** (micrograph, kymographs): left out, no values.
- **Fig. S5B** (frequency histogram of EB1 growth speeds, n = 103): `figs5b_eb1_hist_fig`, grey bars 25 nm/s
  wide; binned mean 164.5 against the printed 165 +- 7.5 nm/s. The arrow is not read.
- **Fig. S5C-D** (cell length and nucleus position, mean +- SD beside each group): `figs5c_length_fig`,
  `figs5d_nucleus_fig`, read as points with error bars at x = group index + 0.25 (the mean +- SD markers stand
  between the category tick and the next minor tick; the x axis is calibrated on the ticks at half-index
  steps 0.5-3.5). The individual cells are not read (as above).

## What the readings check

- The base-condition simulation, picked out of Figs. 4A-B, 5A-B, 6C-D, 7C-D, S1A-B and S3A-B by `pick_*`
  processing models, reproduces the printed mu_sim = 7.27 +- 0.80 and v_sim = 0.37 +- 0.04 everywhere.
- Histogram totals and binned means are set beside the printed n and means (`hist_stats_*`, `hist_mean_eb1`).
- The simulated drug, motor and clutch predictions (Figs. 4A-B, 5A-B, 6C-D, 7C-D, S1, S3) are recorded as
  data with no run: the 1D CMS is not runnable here (q_cms_not_runnable). The measured values (Figs. 4C-D,
  5C-D, 6A-B, 7A-B, S5) wait for a model that predicts them.
