# Figures of vink2024: what was read and what was not

The first reading could not render pages and digitized nothing; that table is replaced by this figure pass
(2026-11-11). Every plotted panel with values is now read by the record's own code (`mode: code`, `figures/`),
with its calibration from the image itself. Each reading was checked with `boxgraph figure check` and its overlay
inspected (`figwork/<reading id>.png`, not committed). All figures are embedded rasters. Those on p. 5 are sharp.
The supplement's (pp. 12-19, a converted .docx) are coarse, about 8 rendered px per source pixel at 1200 dpi.

**How the bar charts are read** (`figures/_bars.py`, all bar panels):

- y calibration: the left-pointing major ticks of the y axis are matched to the printed labels, with a straight-line
  fit; misfit 0.5-2.4 px.
- Bars: found from their black side outlines rising from the x axis.
- Value: the outer (top) edge of the bar's top outline. On the image, the midpoint of every symmetric SD bar falls
  on that edge, within 0-2 px on p. 5; the outline's centre lies 6-7 px lower.
- Interval: the edge blur plus the misfit, widened to include the error bar's midpoint. In the coarse supplement
  rasters the midpoint can lie up to 11 px off.
- Error bars: both caps are read (cap rows, not dots, by their width), and widened by the cap thickness.

x is the study state: 1 baseline, 2 hyperinsulinemia, 3 dobutamine stress (quantity `study_state_index`).

**How the scatter plots are read:**

- Prism panels (`figures/_scatter.py`): the y ticks as for the bars, and the x ticks below the x axis. Markers come
  from a colour mask (red dots for ANOCA, blue triangles for controls). Fused markers are counted by area and split
  by k-means.
- SPSS panel (`figures/_sfig2.py`): y from the grey gridlines. x from the centres of the x labels, since the axis
  has no ticks; label-centring uncertainty is in the note. Hollow rings are joined by dilation and filled, then
  counted and split as above.

The ring and marker thresholds were set by looking at the overlays: arcs read as two rings, a fused pair read as
one. They were not tuned to the printed r.

## Main text (p. 5)

- **Fig. 2A**: read. `fig2a_anoca` (red, bars 1/3/5) and `fig2a_control` (blue, bars 2/4/6), with SD bars.
  - Misfit 0.5 px.
  - All six bars and their SD bars agree with the means and SDs of 3.2 within the reading interval. The verdicts of
    `cmp_fig2a_*_means` are "close" only because a read bar is judged at the printed 3-decimal precision
    (`q_fig_vs_text_precision`).
  - Run `mvr_by_state` on these bars against Fig. 3A (`cmp_mvr_fig2a_fig3a_*`, approximation).
  - The individual dots (one per participant) overlap within each bar and are not read.
- **Fig. 2B**: read. `fig2b_epi`, `fig2b_mva`, `fig2b_inc`, `fig2b_neg` (12 bars, 4 entities × 3 states), with SD
  bars. Misfit 0.5 px.
  - The epicardial-spasm insulin bar has a single dot and no error bar.
  - New data: MBV by CFT entity, printed nowhere else.
  - The bars bear on `q_fig2b_legend`: two, one and two dots for "n=11" support 3 patients. They also show equal
    epicardial-spasm and microvascular-angina means at two states (`q_fig2b_entities`).
- **Fig. 3A**: read. `fig3a_anoca`, `fig3a_control`: MVR means ± SD at states 2 and 3. Misfit 0.7 px.
  - Compared, as an approximation, with the ratio of the Fig. 2A bars and of the printed MBV means (`mvr_by_state`).
    The text's medians are a different statistic (`q_fig3_means`).
- **Fig. 3B**: read. `fig3b_anoca`, `fig3b_control`: M-value means ± SD (axis μmol/kg/min), placed at state 2.
  Misfit 0.9 px. The text prints medians in mol/kg/min (`q_mvalue_unit`, `q_fig3_means`). No model.
- **Fig. 3C**: read. `fig3c_anoca`, `fig3c_control`: heart rate reserve means ± SD (axis without unit), placed at
  state 3. Misfit 0.9 px.
  - Against 54.8 ± 21.6 and 67.1 ± 11.9 BPM (3.5): ANOCA reproduced, controls "close" at the printed precision; SD
    bars match.
  - The lower x axis line below 0 is not the bars' base: the base is taken at the y = 0 tick.
- **Fig. 1**: left out. Echo frames with ROIs: a drawing, no values.

## Supplement

- **Suppl. Fig. 1** (p. 12): left out. ROI map and coronary territories: a drawing.
- **Suppl. Fig. 2** (p. 13): read. `sfig2_patients` (28 red rings) and `sfig2_controls` (26 blue rings): observer 1
  against observer 2 baseline MBV. `sfig2_line` is the drawn line at x = 0.20 and 0.70.
  - Calibration: 6 gridlines, misfit 1.2 px; 6 label centres, misfit 2.4 px.
  - 54 rings found; 3.2 gives 55 baseline values, so one ring is likely fully covered.
  - `r2_interobserver` on the rings reproduces the legend's R2 Linear = 0,690.
  - `ols_line` reproduces the drawn line, and `identity_line` (y = x) does not. The caption's "perfect agreement" line
    is the regression fit (`q_sfig2_line`).
  - The ICC (0.87) is not recomputed: its form (one- or two-way, single or average) is not stated.
- **Suppl. Fig. 3A-C** (p. 14): read. `sfig3{a,b,c}_{anoca,control}`: MBV per coronary territory (LAD, RCA, CX) by
  state, with SD bars.
  - Misfit 2.2 px (A), 0.5 px (B, C). The coarse raster puts some SD-bar midpoints 5-11 px above the bar edge; the
    intervals include both.
  - New data (territory MBV). `territory_mean` (equal weights) against the whole-myocardium means: within about
    0.004 for ANOCA, but 0.504 against 0.476 for controls at stress (`q_territory_weights`).
- **Suppl. Fig. 4** (p. 15): read. `sfig4_anoca`: 21 red dots, baseline MBV against HMR. Misfit 1.8 px (x),
  0.5 px (y).
  - Two fused pairs split.
  - `r_hmr_mbv` reproduces the printed r = 0.268.
- **Suppl. Fig. 5A** (p. 16): read. `sfig5a_anoca`, `sfig5a_control`: MBF means with error bars (kind unstated,
  `error_bars: unstated`). Misfit 2.4 px.
  - Every bar holds Supplemental Table 3's mean within its interval. The error bars match the table's SDs. The axis
    label "dB/sec" is therefore a label on the table's numbers (`q_mbf_unit`, `q_fig_vs_text_precision`).
  - Run `fold_by_state` against Suppl. Fig. 5B.
- **Suppl. Fig. 5B** (p. 16): read. `sfig5b_anoca`, `sfig5b_control`: fold MBF means with error bars, at states 2
  and 3.
  - The crop starts below the legend, so the "8" tick is not used; labels 6-0, misfit 0.5 px.
  - Compared, as an approximation, with ratios of the 5A bars and of Supplemental Table 3's means.
- **Suppl. Fig. 6** (p. 17): read. `sfig6_{epi,mva,inc,neg}`: M-value by CFT entity, error bars of unstated kind.
  - The x axis is dotted, so the bars' base is the 0 tick row; misfit 1.6 px.
  - The epicardial-spasm bar is a single dot without an error bar (`q_fig2b_entities`).
  - The printed P = 0.709 is an ANOVA p and is not recomputed (`q_sfig6_p`).
- **Suppl. Fig. 7A-B, 8A-B** (pp. 18-19): read, partially. `sfig7a_*`, `sfig7b_*`, `sfig8a_*`, `sfig8b_*`, red and
  blue separately.
  - The crops of 7A and 8A end left of the legend, which sits inside the plot area, so their 150 tick is not used.
  - Red dots fuse into chains and cover blue triangles: 47, 51, 43 and 43 markers found.
  - `r_mvalue_mvr`, `r_mvalue_fold`, `r_hrr_mvr`, `r_hrr_fold` on the pooled points differ from the printed r by
    0.03-0.04: not reproduced, a limit of the reading (`q_scatter_fused`).
  - The points are still per-participant measurements (M-value, HRR, MVR, fold MBF) for later models.

## Bearing on open questions

- `q_fig2b_legend`: supported, through the dot counts in Fig. 2B and Suppl. Fig. 6 (new `q_fig2b_entities`).
- `q_mbf_unit`: the figure plots the same numbers as the table, so the "dB/sec" label does not change the values.
  Which unit is meant stays open.
- `q_mvalue_unit`: Fig. 3B's axis is μmol/kg/min and its bars are means (38.7, 64.8), not the text's medians.
- `q_ratio_medians`: the figures give means of ratios, not medians, so they neither confirm nor refute it
  (`q_fig3_means`).
- `q_sfig6_p`: not settled by the figure (an ANOVA p is not recomputable from bar means).
