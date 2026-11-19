# Figures of trushko2020

Every reading is by the record's own code (`mode: code`), rendered at 1200 dpi (Fig. S1G at
1000 dpi). Fig. 4H and 4I use `figures/_fig4.py` (first pass); all other readings use
`figures/_cal.py` (axis lines, tick marks, calibration fitted per axis, markers, curves, error
bars) and one shared module per figure (`_fig3df.py`, `_box.py`, `_fig3j.py`, `_fig4fj.py`,
`_fig5f.py`, `_fig6.py`, `_figs2.py`, `_figs5.py`, `_figs6.py`). Calibration is always from the
tick marks matched to the printed labels; "misfit" below is the rms of the tick fit in pixels at
the reading's dpi (the readings add twice it to every interval). Every reading was checked with
`boxgraph figure check` and its overlay (`figwork/<reading id>.png`).

## Main article

- **Fig. 1A-E, 1G**: left out, schematic and micrographs.
- **Fig. 1F**: read, `fig1f_cells` (black dots, mean cell number against time, SD bars, 23 points;
  the first dot is half hidden by the y axis and read without its bar, the last is cut by the plot
  edge and centred on the cut). Misfit 1.1 / 0.9 px. The least-squares slope (`growth_rate_fit`) is
  compared with the printed 3.6 ± 0.1 cells/h: not reproduced (q_growth_rate_fit).
- **Fig. 2**: left out, micrographs.
- **Fig. 3A-C, 3H-I**: left out, schematics, micrographs, contours of one capsule.
- **Fig. 3D**: read, `fig3d_1`, `fig3d_1p5`, `fig3d_2`, `fig3d_2p5` (dots of each concentration
  with their SEM band; the y axis is broken below 0.8 and only the ticks above the break are used).
  Misfit 1.4 / 1.3 px. Dots hidden under another series' band are missing; a band is read only
  where both ends meet the paper.
- **Fig. 3E**: read, `fig3e_boxes` (middle line of each box with the box edges as the bar; the
  52 points of the 1.5% group overlap too much to be told apart). Misfit 0.8 / 1.0 px. The legend's
  means (7.1, 11.5, 20.7, 19.5 kPa) are recorded as printed data; the box line is not compared with
  them, as the legend does not say what it shows.
- **Fig. 3F**: read, `fig3f_1`, `fig3f_1p5`, `fig3f_2`, `fig3f_2p5` (as 3D). Misfit 1.0 / 1.4 px.
  The axis label "-0.1" at the crossing is taken as -100 Pa (q_fig3f_axis_label).
- **Fig. 3G**: read, `fig3g_pressure` (four dots with SEM bars). Misfit 1.2 / 1.2 px. The 1% point
  agrees with the text's 128 ± 6 Pa; the 2.5% point (about 35 Pa) lies outside the text's "between
  50 and 100 Pa" (q_fig3g_range).
- **Fig. 3J**: left panel a schematic; right panel read, `fig3j_indent` and `fig3j_withdraw` (one
  representative force-indentation curve). Misfit 1.0 / 1.0 px. No model: one capsule, no printed
  value to compare.
- **Fig. 3K**: read, `fig3k_points` (44 red points, x = rank). Misfit 1.0 px. The tick steps are
  confirmed by the box lines printed with their values. Mean of the points against the text's
  0.03 ± 0.003 N/m and the 0.033 printed beside the box's square: reproduced; 44 points found, as
  the text's n.
- **Fig. 3L**: read, `fig3l_points` (20 red points). Misfit 1.1 px. Mean against the text's
  128 ± 6 Pa: reproduced; 20 points found.
- **Fig. 4A-E, 4G**: left out, micrographs, drawings, simulated shapes (4E is a grid of shapes).
- **Fig. 4F**: read, `fig4f_delta` (blue, left axis) and `fig4f_phi` (red, right axis), right of the
  break of the time axis only. Misfit 1.5 / 1.2 (delta) and 0.7 (Phi) px. A few dots hidden under
  the other series are missing.
- **Fig. 4H**: first pass read the two theory curves (`fig4h_alpha`, `fig4h_gamma`); this pass adds
  the 24 blue measured dots, `fig4h_phi` (the legend dot is left out). They are the same folds as
  the red dots of Fig. 6B (`fig6b_exp`), and the two readings agree point by point within their
  intervals. The paper claims only that they lie between the alpha and gamma curves; no comparison.
- **Fig. 4I**: first pass (`fig4i_alpha`, `fig4i_phi`), unchanged.
- **Fig. 4J**: read, `fig4j_empty` (black) and `fig4j_tissue` (red), x = rank. Misfit 1.0 px.
  30 of 31 and 16 of 17 points found; the means agree with Table 1, not with the five-digit means
  printed on the figure (q_fig4j_means_reading).
- **Fig. 5A-E**: left out, model drawing, simulated shapes, micrographs.
- **Fig. 5F**: read, `fig5f_exp` and `fig5f_sim` (bar heights per fold number). Misfit 1.0 / 0.8 px.
  The bars sum to 42.7 and 183.1 against the legend's n = 43 and 184.
- **Fig. 5G, 5H**: left out, polar histograms whose radial count labels are not evenly spaced from
  the centre, so sector lengths cannot be calibrated (q_fig5gh_radial_scale).
- **Fig. 6A**: left out, simulated shapes.
- **Fig. 6B**: read, `fig6b_exp` (24 red dots; one dot cut by the alpha line is rejoined),
  `fig6b_simmean` (dark grey simulation means; chains of touching dots split by area, so these have
  larger intervals), `fig6b_alpha`, `fig6b_gamma` (theory lines). Misfit 1.6 / 1.9 px. The light grey
  cloud of 1,297 points is left out (it overlaps itself). The two lines are compared with the
  record's elastica solution (`fold_elastica`): reproduced, as for Fig. 4H.
- **Fig. 6C**: read, `fig6c_exp` (red dots with SD bars) and `fig6c_sim` (the band of grey simulation
  dots, at chosen x away from the red dots; their thin grey SD bars are not read). Misfit 1.3 / 1.6 px.
- **Fig. 6D**: read, `fig6d_magenta`, `fig6d_blue`, `fig6d_green` (mean simulated pressure; only dots
  found singly, so runs of touching dots, most of the blue series, are missing; the SD bars cannot be
  told from the 41 traces of the same hue and are not read). Misfit 1.3 / 0.9 px.

## Supplemental Information

- **Fig. S1A-F**: left out, photographs, drawings, micrographs.
- **Fig. S1G**: read, `figs1g_means` (the black line of each group; the point swarms and the
  coloured bars run together and are not read). Misfit 0.5 px. The 2.5% line (about 100 um) is
  compared with Table 1's 97 ± 1 um: close (q_figs1_caption_letters, which also notes the shifted
  caption letters).
- **Fig. S2A, C, E**: left out, micrographs.
- **Fig. S2B, D, F**: read, `figs2b_roi1`, `figs2d_roi1`, `figs2f_roi1` (the purple ROI 1 trace).
  Misfit 0.5 px. ROIs 2-4 left out: in B the three traces are noisy and overlap; in D and F they lie
  on the x axis; the insets of D and F hold three overlapping traces.
- **Fig. S2G**: read, `figs2g_unbent`, `figs2g_bent`. Misfit 0.5 px.
- **Fig. S3, S4**: left out, micrographs.
- **Fig. S5A-C**: left out, photographs and contours.
- **Fig. S5D, E**: left out, superimposed radius profiles of many time points that cannot be told
  apart.
- **Fig. S5F, G**: read, `figs5f_thickness`, `figs5g_pressure` (open circles found by ring matching,
  SD bars; a bar end cut by the plot frame is taken as the mirror of the other end, and the reading
  says so; the circle at t = 0 is behind the y axis and missing). Misfit 0.5 px.
- **Fig. S5H**: read, `figs5h_empty` (orange dots; the grey individual traces are not read).
  Misfit 0.5 px.
- **Fig. S6A, D**: left out, drawings.
- **Fig. S6B**: read, `figs6b_l8` ... `figs6b_l4` (the five lines, by their order from the top).
  Misfit 0.5 px (log axes, decade ticks). Compared with Eq. S25 with Eq. S21 (`ring_pressure_s25_normalized`,
  shape only): reproduced for every line, with one and the same implied prefactor.
- **Fig. S6C**: read, `figs6c_lines` (the five lines at kR^2/lambda = 100, x = their lambda R^2/K
  from the legend). Misfit 0.5 px. Compared with Eq. S26 (`pbuckling_s26_normalized`, shape only, one
  prefactor for all five): reproduced. This figure bears on the open question q_eq1_prefactor: the
  prefactor of the paper's own numerics is far from the one the main-text estimate of lambda needs
  (q_s26_numerics_prefactor).
- **Fig. S6E**: read, `figs6e_increasing` (magenta) and `figs6e_decreasing` (green), centres of the
  '+' marks and their SD bars. Misfit 0.5 px. Where the two ramps overlap (Delta eps above 1.6%),
  green stems are partly hidden and some points of both ramps are missing.
- **Fig. S6F**: read, `figs6f_delta` (blue, left axis) and `figs6f_phi` (orange, right axis); blue
  dots drawn under orange ones are hidden and missing (19 blue, 24 orange found). Misfit 0.5 px. The
  fitted lines are not read.
- **Fig. S6G, H, I**: read, `figs6g_alpha`, `figs6h_delta`, `figs6i_force` (the envelope that the
  lambda R^2/K = 10^8 curve and the common line form). Misfit 0.5 px (log axes, minor ticks fitted).
  G and H compared with the small-strain laws Eqs. S18 and S17 (n = 1, added): not reproduced; S18
  is about four times below the numerics (q_s18_numerics). The other four curves of each panel join
  the common line and are not read separately.
- **Fig. S7A, B**: left out, 81 small panels each (fold-number histograms and pressure traces over a
  grid of parameters), each panel about 0.5 cm wide on the page, with tick labels a few pixels high
  at 1200 dpi and up to 41 overlapping traces per pressure panel; too small to read reliably.
