# Figures of sexton2025

A first pass (reader) read no figure (its reasons are kept, where they still apply, below). This figure pass
(2026-11-09) reads every panel that plots values it could separate, with code in `figures/` that calibrates
each axis from the image (tick marks matched to the printed labels; the misfit, in pixels, widens every
interval). Shared code: `_common.py` (frame lines, ticks, axis fits), `_curves.py` (line tracing; a line
partly hidden under a dark frame line gets an interval that extends under it). Misfits below are the
largest distance of a tick from the fitted axis; 0.5 px means the ticks fit to within the pixel.

## Main text

- **Fig. 1A-B, H-K**: renderings of networks and domains, a schematic, a photograph. No values. Left out.
- **Fig. 1C-F**: scatter clouds, one translucent point per generated network (hundreds per panel, both
  colours overlapping); the points cannot be told apart. Left out. Panel F's moving averages are the lines
  of Fig. 1G, read there.
- **Fig. 1G(i), (ii)**: read, `fig1g_lat_i` (blue), `fig1g_vas_i` (orange), `fig1g_lat_ii` (green),
  `fig1g_vas_ii` (red): <C_tissue>/C_inlet against vessel count, moving averages. y axis the line right of
  the colour bar (6 ticks, 1.0-0.0), x a log axis by its long decade ticks 10^1-10^3; misfit 0.5 px both.
  Traced from N = 100 where no inset image touches the lines. The cube's vasculature stays near 0.5-0.56
  out to 3000 vessels while the lattice falls to 0.02 by 1000; in the biventricle both fall (vasculature
  0.41 to 0.21). No model in the record computes advection-diffusion-permeation; nothing compared.
- **Fig. 2A, D, E, G**: schematics and renderings. Left out.
- **Fig. 2B**: read, `fig2b_recompute` (red dashed, "C α N^2") and `fig2b_naive` (red dotted, "C α
  (N*E)^2"); log y by its four long decade ticks (misfit 0.5 px), x ticks 10-80. Both lines are straight
  in these axes; each is found by a RANSAC line through its dash or dot pieces (the same-red labels are
  outvoted), rms 0.5 and 0.04 px. **Compared**: `cmp_fig2b_recompute` runs the caption's own scaling,
  C = C0 (2^(B+1)-1)^2 for a full balanced tree (`balanced_tree_n2`), against the dashed line: it rises
  0.60 decades per depth against the line's 0.046 (q_fig2b_scaling). The blue partial-binding lines (graded
  shades of one blue, one per E, overlapping) cannot be told apart; left out.
- **Fig. 2C**: read, `fig2c_approx` (red) and `fig2c_pb` (blue), the median alignment lines (shading
  min-max not read); y 6 ticks 0.0-1.0, x 10-80; misfit 0.5 px. Partial binding sits under the top frame
  line beyond depth 20 (intervals reach 1.0); at depths < 20 its spikes make the runs thick and the
  intervals cover them. Results of the paper's software, not a model in the record; nothing compared.
- **Fig. 2F**: read, `fig2f_mesh` and `fig2f_implicit` (solid and dashed line of each colour together).
  The top decade label is printed "10^-5" (it must be 10^-3; q_fig2f_axis_label): only the 10^-4 and
  10^-5 ticks are used. Misfit 0.5 px. Timings on the authors' machine.
- **Fig. 2H, 2I**: read the lines only: `fig2h_fit` and `fig2i_fit` (the red lines through the points),
  `fig2h_sphere` (the blue dots, which overlap into one band, traced as a line). The black points with
  their +-2 SD bars (51 per panel) touch their neighbours and their bars cross; a marker reader separated
  only 24 of 51 in 2I and misread several bar ends, so the points are left out (q_fig2hi_points). 2H's y
  axis has 16 equal ticks; every fifth is labelled (0.000-0.015).
- **Fig. 3**: 3D/1D/0D colour maps of specific unreleased trees with no value axis to read. Left out.
- **Fig. 4**: renderings and photographs. Left out.
- **Fig. 5A-E, G, J-O**: photographs, micrographs, schematics, colour maps without a readable value axis.
  Left out.
- **Fig. 5F**: read, `fig5f_piv` (measured: each branch's error bar, its midpoint the mean of N = 3, its
  caps +-1 SD), `fig5f_cfd` (the grey "+" per branch), `fig5f_cfd_mean` (the grey dashed line at each
  branch column). y 8 ticks 0.0-0.7 (misfit 0.59 px), branches by the three x ticks. Embedded raster:
  caps are told from marker edges by width (caps 50-66 px, square edges and triangle bases 70-76 px at
  1200 dpi); the Middle branch's upper cap lies on the triangle's base and is read there (noted). The
  individual markers (circle, square, triangle) overlap each other and the caps (Bottom: square on
  triangle) and were not read; the bar summarises them. **Compared**: `cmp_fig5f_cfd_vs_piv` (validation,
  CFD against PIV). The PIV means add to 0.70, the CFD values to 0.97 (q_fig5f_piv_sum).
- **Fig. 5H(i)**: schematic. **5H(ii)** and **5I**: about ten simulated and theoretical flow curves and as
  many pressure curves per panel, drawn in graded shades of one blue and one red, overlapping, with no
  legend tying a shade to an outlet or cross section: the curves cannot be told apart. Left out.
- **Fig. 5P(ii), bottom**: read, `fig5p2_perfused` (R 0.2-0.95), `fig5p2_media` and `fig5p2_pbs` (only
  where the line stands clear of the thick x axis: near R = 0.8-0.95). Only panel 1 has a y axis (4 ticks
  0-60, misfit 0.5 px); panels 2 and 3 share its baseline and height and are read with its scale (stated
  in each note). The flat stretches lying on the x axis are not traced.
- **Fig. 5P(iii)**: read, `fig5p_count` and `fig5p_viability`: bar tops and upper error bars (the lower
  halves are hidden in the black bars and mirrored). y ticks 0-500 and 0-80, misfit 0.5 px. The media
  control bars are a few pixels tall: their intervals run from 0. **Compared** (consistency) with the
  values printed in the caption and above the bars: `cmp_fig5p_count_bars` (417 ± 37, 1.0 ± 0.4) and
  `cmp_fig5p_viability_bars` (37.8 ± 33.6 %, 0.4 ± 0.4 %).
- **Fig. 5P(i), (ii) top**: images. **5P(iv)**: a heat map whose values are printed in its cells (KL
  divergences); they are printed numbers, not plotted values, and are not entered here. **5P(v)**: 13
  radial profiles whose legend reuses colours (regions 1 and 8, 2 and 9, ... share a hue): the curves
  cannot be assigned. **5P(vi)**: a polar plot; not read in this pass (no polar calibration).

## Supplementary figures

- **Fig. S1**: colour-mapped renderings of lattice flows and pressures; no value axis to read. Left out.
- **Fig. S2A-C**: schematics. **S2D-F**: read, all nine mean lines: `figs2d_array`, `figs2d_linked`,
  `figs2d_vectorized`, `figs2e_array`, `figs2e_linked`, `figs2f_array_any`, `figs2f_array_all`,
  `figs2f_linked_any`, `figs2f_linked_all` (shading +-2 SD not read). y labels carry the printed factor
  (x10^-2, x10^-4, x10^-3); S2E has one unlabelled tick above 8.0, dropped by matching from the x axis up.
  Misfits 0.5-1.8 px. **S2G**: a broken y axis (two scales) with a blue line along the lower part and an
  orange line whose shading fills the panel; not read in this pass.
- **Fig. S3**: 24 small panels (8 optimizers x time, volume error, alignment error, with +-1 SD bands);
  not read in this pass. The paper's choice (L-BFGS-B) is argued in the text.
- **Fig. S4A**: a matrix. **S4B**: read, `figs4b_pu` and `figs4b_global` (log-log; the lines cross near
  1500 points, bridged). **S4C-D**: box plots by patch size; not read in this pass.
- **Fig. S5, S6, S9**: renderings of reconstructed domains and trees. Left out.
- **Fig. S7A, C**: slices and renderings. **S7B**: percentages printed as text in the figure (not
  plotted values); not entered.
- **Fig. S8**: read, `figs8_upper` and `figs8_lower`, the two dark red lines (convex domains) at 100,
  1000, 4000, 8000 terminals: the line's height from the straight segments either side of each point,
  the +-1 SD bar from the red run through the point (at 100 terminals the two lines' bars overlap and are
  not read). Log axes by decade ticks, misfit 2.5 px on y. The ~208 blue lines overlap into one band;
  left out.
- **Fig. S10A-B**: read, `figs10a_1e4/1e5/1e6`, `figs10b_1e4/1e5/1e6`: histogram bins where each colour's
  top is visible (bins covered by a later-drawn colour, and the legend swatches, are not read). Axes misfit
  0.5 px. The x axes are in cm, which settles q_fig_s10_units (q_fig_s10_units_axis). The caption's means
  are not recomputed from the bins.
- **Fig. S11A-B**: images. **S11C**: read, `figs11c_bottom`, `figs11c_middle`, `figs11c_top`: the three
  parabolic fits (solid lines); the hundreds of pale, overlapping measured squares cannot be told apart and
  are left out. The fits are consistent with v = v_max (1 - r^2/R^2) to the dashed channel boundaries
  (e.g. Bottom 670 um/s at 0, 401 at +-500 um; R ~ 790 um), checked by eye only.
- **Fig. S12**: 15 small panels of 3D FSI waveforms (two series of dense markers each) for an unreleased
  network; not read in this pass.
- **Fig. S13, S14**: schematics and photographs. Left out.
- **Fig. S15A(i)**: read, `figs15a_live` and `figs15a_dead`, every bar standing on the axis (bins every
  ~20 um^2, the spacing read from the bars; bars a few pixels tall, above ~700 um^2, are not found). y
  ticks 0-800, x by the 15 labelled ticks 60-900. **S15A(ii)**: violin plots (the caption prints their
  means and SDs). **S15A(iii), B, C(i-iii)**: images. **S15C(iv-vi)**: miniature copies of Fig. 5P(v-vi)
  with illegible labels. Left out.
