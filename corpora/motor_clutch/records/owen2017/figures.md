# Figures of owen2017: what was read and what was not

Three passes on 2026-11-22. The first could not render pages and read nothing. The second wrote the
calibrated readings of Fig. 2D-H, 3B, 3C, 3G (line plot), 4A, 4B, 4F, 5B, 5C, 6B and Supp. Fig. S9B, S10,
S12, S14C-E, S16B/D and S17, with the shared code `figures/_kit.py`, `_curve.py`, `_hist.py`, `_rose.py`,
`_ends.py` and `_s10.py`. The third (this file) kept those unchanged and added Supp. Fig. S2 (left column),
Supp. Fig. S11, the rose insets of Fig. 3G and 4A, and three rows of the density map of Fig. 4E
(`figures/_s2.py`, `_rose_k.py`, `_heat.py`).
Every reading was run with `boxgraph figure check`, and its overlay in `figwork/<id>.png` was looked at.
"Misfit" is the largest residual of the axis calibration, in pixels at the reading's dpi. Every value's
interval includes twice the misfit.

## Main article

- **Fig. 1** (p. 3): left out. Confocal images, renderings and displacement maps; no axes with values.
- **Fig. 2A-C** (p. 4): left out. Images, a quiver plot and a 3D rendering.
- **Fig. 2D-H, profiles** (p. 4): read: `fig2d_disp_mag`, `fig2e_disp_normal`, `fig2f_disp_tangential`,
  `fig2g_disp_parallel` and `fig2h_protrusion_strain` (second pass; median line with its 1 SD band, at 10 distances
  from the tip). The y axes carry only two labels each; unlabelled minor stubs were snapped to the label step, which
  leaves y misfits of 13-20 px in D, F and G (1.4 px in E, 0 in H) and wide intervals there. x misfit 1-1.2 px.
  The cell maps beside the profiles are left out (renderings). No model in the record predicts these profiles.
- **Fig. 3A, D-F** (p. 5): left out. Track images, image montages and kymograph-like strips.
- **Fig. 3B** (p. 5): read: `fig3b_pax`, `fig3b_fib` (bar by bar, 40 bins; misfit x 1.8, y 2.2 px). Binned means
  compared with Table 1 rows 8-9 (reproduced, close).
- **Fig. 3C, histogram** (p. 5): read: `fig3c_slip` (misfit x 1.4, y 0.83 px). Its binned mean against Table 1
  row 10 is close.
- **Fig. 3C, rose inset**: left out. The inset is transparent over the bars, its rings are grey 235-240 on white,
  and the wedge outlines (about 6 deg wide) are barely darker than their fill and blur together near the centre.
  The wedges cannot be read reliably.
- **Fig. 3G, line plot** (p. 5): read: `fig3g_angle` (markers with the 95% confidence band; misfit x 0.39,
  y 0.47 px).
- **Fig. 3G, rose inset** (p. 5): read: `fig3g_rose` (third pass; 20 wedges of 18 deg; rings 20/40/60 tracks,
  two labelled, ring misfit 0.86 px; the search is kept inside the inset, away from the line plot's band). These
  are the paxillin angle counts behind "relatively few motions perpendicular to the protrusion axis". They bear on
  `q_no_continuous_rearward_flow`: the retrograde wedges (171 and 189 deg, about 53 and 51 tracks) and anterograde
  wedges (351 and 9 deg, about 19 and 34) are both large, so paxillin plaques move both ways, as the text says.
- **Fig. 4A, histograms** (p. 7): read: `fig4a_fib`, `fig4a_actn` (misfit x 0.35, y 0.5 px). Binned means against
  Table 1 rows 11-12 are not reproduced (`q_fig4a_hist_mean`; the actinin histogram is cut at 200 nm/min).
- **Fig. 4A, rose inset** (p. 7): read: `fig4a_rose` (third pass; 30 wedges of 12 deg; rings 500 and 1000, both
  labelled, ring misfit 0.4 px; navy outlines in a blurred raster, read inside the inset only). Angles between
  α-actinin-1 and adjacent fibrin velocities: they peak at 0 deg (parallel).
- **Fig. 4B** (p. 7): read: `fig4b_rose` (second pass; ring misfit 0.82 px). Its outlines are coloured and its
  fill follows them (checked this pass against the polygon-fill fault found in S11; not present).
- **Fig. 4C, D** (p. 7): left out. Velocity maps on the cell surface and a kymograph.
- **Fig. 4E** (p. 7): read: `fig4e_cos_p1`, `fig4e_cos_0`, `fig4e_cos_m1` (third pass; the counts of puncta
  pairs in the cos(theta) = 1, 0 and -1 rows at 14 distances, by colour against the colour bar). The map has 21
  rows of 0.1 in cos(theta); the labels 1 and -1 sit at the centres of the top and bottom rows, and the colour steps
  in the column at 20 um lie within 2.7 px of that grid. x from the 11 tick stubs (0 at the y axis, 100 at the
  frame); the printed x labels sit 10-26 px left of their ticks. Colour: the nearest colour on the bar (its ends
  labelled 0 and 3); the interval spans the bar positions within 8 RGB units of it. The bar is labelled
  "bin counts x 10^-3", read as counts times 10^-3 shown, so values are stored as counts (bar value times 1000).
  If the label meant the opposite convention, every value would be 10^6 times smaller; Fig. 4F's "10^3
  correlations" per distance bin is consistent with thousands. The other 18 rows are not read: they are
  near-uniform blue and add little beyond the three read.
- **Fig. 4F** (p. 7): read: `fig4f_dircorr` (median with SE band; misfit x 0.61, y 0.27 px).
- **Fig. 5A, D** (p. 8): left out. Tracks coloured by time and image montages.
- **Fig. 5B** (p. 8): read: `fig5b_actn`, `fig5b_pax` (misfit 0.2 px). The paxillin binned mean reproduces
  Table 1 row 1.
- **Fig. 5C** (p. 8): read: `fig5c_rose` (second pass; ring misfit 0.83 px).
- **Fig. 6A, C** (p. 9): left out. A network rendering and a schematic.
- **Fig. 6B** (p. 9): read: `fig6b_steepest` (the steepest line, misfit x 0.39, y 0.46 px) and `fig6b_ends`
  (where each of the 19 lines ends). The steepest line is compared with the printed "up to ~24 nN/um" (close).
  `fig6b_ends` is not compared: the network model is not runnable (`q_network_not_runnable`). It is the record of
  the spread of node stiffness (`q_node_stiffness_spread`).

## Supplemental Material

- **Supp. Fig. 1** (p. 24): left out. A quiver map.
- **Supp. Fig. 2** (p. 25), **left column** (example cell 1, 7 profiles): read: `figS2_cell1_disp_mag`,
  `figS2_cell1_disp_normal`, `figS2_cell1_disp_tangential`, `figS2_cell1_disp_parallel`,
  `figS2_cell1_protrusion_strain`, `figS2_cell1_lagrange_strain`, `figS2_cell1_shear_strain` (third pass; one
  600 dpi crop of the column, which is about the page's own raster resolution). Each is read at the 18 plotted
  vertices (2.5 to 87.5 um), with the SD band as error bar. y is calibrated from the panel's own labelled stubs
  (misfit 0-0.4 px). x is set by the bottom panel's y axis (0) and its one tick (50), with a 1.5 px allowance.
  The printed "100" has no tick and sits where the tick scale gives about 87.5 um (`q_figS2_x_labels`; the caption's
  "2 μm bins" fit neither scale). The cell rendering above the top panel reaches into it; the band, not the dark
  drawing, is taken in each column.
- **Supp. Fig. 2, columns 2-6** (four more cells and the summary over N = 7 cells, n = 10 protrusions): left out.
  Their y axes have tick marks but no labels, at rows and spacings that differ from the labelled left column's in
  the same row (measured: e.g. row 2, column 1 stubs every 102 px from row 554, column 3 every 98 px from row 675),
  so each panel has its own limits and no value can be assigned (`q_figS2_unlabelled_columns`). The summary column
  is the one the main text relies on; it would need the authors' axis limits.
- **Supp. Fig. 2, top row**: left out. Cell renderings.
- **Supp. Fig. 3-8** (pp. 26-33): left out. Images, renderings and stainings.
- **Supp. Fig. 9A** (p. 33): left out. A drawing. **9B**: read: `figS9b_pax`, `figS9b_actn` (every dot; misfit
  x 0.49-0.81, y 0.65 px). No runnable model uses them (Supp. eqn. 2 lacks inputs, `q_localization_inputs`).
- **Supp. Fig. 10** (p. 34): read: `figS10_Gp_cells`, `figS10_Gp_nocells`, `figS10_Gpp_cells`, `figS10_Gpp_nocells`
  (every marker; misfit x 1.1, y 0.2-1.4 px).
- **Supp. Fig. 11** (p. 35): read: `figS11_cell01` ... `figS11_cell18` (third pass; one rose per cell, 20 wedges of
  18 deg each, read from the black outlines; ring misfit 0.16-1.3 px). Only the outer ring is labelled; the inner
  ring is taken as half (`q_figS11_reading`). The bin width is fixed at 18 deg: roses 1-5 give it by
  themselves, while sparse roses mislead the automatic choice. The blue fill is drawn as one polygon over the
  outline path and spills outside the wedges (roses 9, 16), so it is not used. Rose 13's "30" is an angle label,
  and labels are dropped because only the outline connected to the centre is used. No wedge is cut by the plot box.
  These per-cell counts are the data behind `q_no_continuous_rearward_flow`: each cell's retrograde
  (about 180 deg) and anterograde (about 0 deg) wedges can now be compared cell by cell. No model in the record
  predicts them.
- **Supp. Fig. 12** (p. 36): read: `figS12_parallel`, `figS12_opposite` (CDFs; misfit x 0.54, y 0.51 px).
- **Supp. Fig. 13** (p. 37): left out. Phase-contrast montages and stainings.
- **Supp. Fig. 14A, B** (p. 38): left out. A montage and a cartoon. **14C**: read: `figS14c_actn`, `figS14c_zyx`
  (misfit x 0.64, y 1.2 px; binned means reproduce Table 1 rows 3-4). **14D**: read: `figS14d_rose` (ring misfit
  0.58 px). **14E**: read: `figS14e_rel`, `figS14e_diff` (misfit x 1.4, y 0.79 px). Their binned means do not
  reproduce Table 1 rows 5-6 (about 70 against 58 ± 3.1, and 35 against 29 ± 1.8 nm/min; `q_spooling_hist_mean`).
  This bears on `q_validation_mean_vs_range`: eqn. 13 is validated against the table's 58 nm/min, but the plotted
  distribution's mean is higher.
- **Supp. Fig. 15** (p. 39): left out. Stainings.
- **Supp. Fig. 16A** (p. 40): left out. A network rendering. **16B, D**: read: `figS16b_ends`, `figS16d_ends` (line
  ends), not compared (network not runnable).
- **Supp. Fig. 17** (p. 41): read: `figS17_v` (misfit x 0.0002, y 0.02 px), with eqn. 13 swept over its 13 x
  positions: reproduced. For alpha_c <= -0.5 the curve runs slightly below zero, where the stated condition sets
  v = 0 (`q_figS17_unclamped`).

## Measurements without a model in the record

Recorded as data for later papers' models: the profiles of Fig. 2D-H and Supp. Fig. 2 (left column), the rose
plots (Fig. 3G, 4A, 4B, 5C, S11, S14D), the directional correlation and pair counts (Fig. 4E, 4F, S12), the rheology (S10) and the
localization error (S9B). The record's clutch model (eqn. 13) gives one speed per adhesion and no direction, so it
predicts none of the angle distributions.
