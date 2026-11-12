# Figures of mohammed2015

Figure pass of 2026-11-11. The first reading job could not render pages (see `q_figures_not_read`); this
pass reads every figure that plots values. All readings are `mode: code` and share `figures/_kit.py`:

- **Calibration**: the axis line is the longest run of ink; the tick marks are the ink runs in a thin strip
  just outside it, matched in order to the printed labels the reading file lists; a least-squares line maps
  pixel to value, and its largest residual at a tick (the misfit) is added to every interval.
- **Histograms** (`histogram`): the bar of one colour beside each x tick (black left of the tick, red right),
  read at its top edge over the middle half of its columns. Interval ± (JPEG blur at the edge, at least
  2.5 px, + 1.5 px) + misfit. A bar only a few pixels tall is found by its tint (`soft_masks`) and read with
  an interval from the axis line to 4 px above the tint; an empty bin reads 0 with an interval of 3 px.
- **Tukey box plots** (`boxes`, `read_boxes`, `read_box_stats`): a box is a component of one colour with two
  wide lines joined by both sides and hollow inside; its top, inner and bottom lines give Q3, median and Q1;
  the whisker ends are the caps (the outermost wide row group along the whisker), read at their centre with
  an interval of half the cap's row extent + 1 px. Where outlier points touch a cap the note says so and the
  interval covers the merged rows.
- **Scatter plots** (`scatter`): round markers of one colour; touching markers are separated by greedily
  fitting discs of the marker radius; interval ± 1 px for an isolated marker, ± 0.25 R in a cluster.

The main-paper figures are JPEG rasters of low native resolution (about 2 render px per source pixel at
1200 dpi in Fig. 1, about 6 in Fig. 2B), so intervals are wider than the render resolution suggests; the
supplement figures (pp. 24-26) are clean.

## Panels

- **Fig. 1A** (p. 5), heart weight histogram: read, `fig1a_control` (black), `fig1a_hfpef` (red), 15 bins
  150-850 g; y on 6 ticks, misfit ~0. Data `fig1a_*_fig`; medians by `hist_median_hw` against Table 2
  (`cmp_fig1a_*_median`, approximation).
- **Fig. 1B** (p. 5), % expected heart weight: read, `fig1b_control`, `fig1b_hfpef`, 7 bins; misfit 0.11
  points; the 350 HFpEF bar is faint (tint). Medians against Table 2 (`cmp_fig1b_*`).
- **Fig. 1C** (p. 5), CAD sum score: read, `fig1c_control`, `fig1c_hfpef`, 9 bins 0-16; misfit 0.04. Medians
  against Table 2's 'coronary artery stenosis total score' 6 and 12 (new data `cad_c_med`, `cad_h_med`).
- **Fig. 1D** (p. 5), number of vessels > 50% stenosis: read, `fig1d_control`, `fig1d_hfpef`, 0-4; misfit ~0.
  The share with ≥ 1 vessel (`share_any_stenosis`) is checked against the abstract's 13% and 65% and the
  Results' 77 (65%) (`cmp_fig1d_*`).
- **Fig. 2A** (p. 6), MVD histogram: read, `fig2a_control`, `fig2a_hfpef`, 10 bins 100-1900; misfit 0.10.
  The bars total about 107% (control) and 126% (HFpEF), unlike every other histogram here (99-102%):
  `q_fig2a_bars_total`. Medians (bars normalised to their own total) against Table 2.
- **Fig. 2B** (p. 6), MVD by wall layer (Epi, Midwall, Endo, Pap), Tukey boxes: read,
  `fig2b_control_{median,q25,q75,whisker_lo,whisker_hi}` (black) and `fig2b_hfpef_*` (red), x = wall region
  1-4; y on 4 ticks, misfit 7 vessels/mm2. Worst raster of the paper; outlier clusters touch most caps, so
  the whisker ends carry wide intervals. **The Epi and Endo boxes are identical** in both groups (same
  quartiles, whiskers and outlier pattern): `q_fig2b_epi_endo_identical`. No regional value is printed, so
  nothing to compare with.
- **Fig. 2C-D** (p. 6): left out, micrographs (CD31 stain), no values.
- **Fig. 3A** (p. 6), % fibrosis histogram: read, `fig3a_control`, `fig3a_hfpef`, 11 bins 0-40; y on 3
  ticks, misfit 0.10; the HFpEF bars at 32 and 40 are faint. Medians against Table 2.
- **Fig. 3B** (p. 6), log % fibrosis against MVD, ~228 points: left out, the black and red points overlap in
  one dense cloud where individual points cannot be separated; the fitted lines and printed statistics
  (R2 0.15) are not reproducible from a partial reading.
- **Fig. 3C-F** (p. 6): left out, stained sections, no values.
- **Fig. 4A** (p. 7), MVD Tukey boxes: read, `fig4a_{median,q25,q75,whisker_lo,whisker_hi}` (x 1 control,
  2 HFpEF) and `fig4a_hfref` (the blue HFrEF box, x = statistic 1-5); y on 6 ticks, misfit 3.7
  vessels/mm2. Against Table 2 (`cmp_fig4a_*_t2`, new table data `mvd_t2_*_tab`): control 1148 / 1316 /
  1467 and the HFpEF median and Q1 reproduce; **the HFpEF Q3 does not: the box top is near 1190, not the
  printed 1370**. This settles `q_mvd_h_q75` (see `q_fig4a_hfpef_q75`). The HFrEF box is printed nowhere
  else.
- **Fig. 4B** (p. 7), % fibrosis Tukey boxes: read, `fig4b_*` and `fig4b_hfref` as for 4A; misfit 0.09.
  Every Table 2 median and quartile reproduces (`cmp_fig4b_*_t2`).
- **Fig. 4C** (p. 7), log % fibrosis against MVD with HFrEF: left out, overlapping points as in Fig. 3B.
- **Figs. S1-S4** (pp. 20-23): left out, method illustrations (processing steps, size classes, regions,
  fibre orientation), no plotted values.
- **Fig. S5A** (p. 24), MVD by hypertension history: read, `figs5a_*`, x 1 CON no HTN, 2 CON HTN, 3 HFpEF
  no HTN, 4 HFpEF HTN; misfit 3.1 vessels/mm2. No value printed to compare with.
- **Fig. S5B** (p. 24), % fibrosis by hypertension history: read, `figs5b_*`; misfit 0.065.
- **Fig. S6** (p. 25), LV mass and E/e' against MVD in HFpEF: read, `figs6_lvm` (75 of the n = 78 markers),
  `figs6_ee` (29 of 30); misfit x 0.14 / 0.06 vessels/mm2, y 0.28 g / 0.03. The Pearson r of the read
  markers (`pearson_r_lvm`, `pearson_r_ee`) is compared with the printed r = -0.29 and -0.42 (text and
  Table S3); markers that coincide cannot be separated (`q_figs6_hidden_markers`). The regression lines are
  not read.
- **Fig. S7** (p. 26), QRS and QTc against MVD and fibrosis, control and HFpEF: left out, about 228 small
  points per panel in two colours whose dense centres overlap; individual points cannot be separated.

## Open questions this pass settles or raises

- `q_mvd_h_q75` (Table 2's HFpEF upper quartile 1370): settled by Fig. 4A, see `q_fig4a_hfpef_q75`.
- `q_figures_not_read`: superseded by this pass (its text is kept as written).
- New: `q_fig2b_epi_endo_identical`, `q_fig2a_bars_total`, `q_figs6_hidden_markers`, `q_fig1_hist_bins`.
