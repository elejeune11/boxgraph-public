# Figures of campbell2011

- **Fig. 1 (p. 4)**: photomicrographs (picrosirius red, reticulin, CD31). Left out: no values to read.

Fig. 2 (p. 5) has four scatter plots of per-patient values: men as open circles, women as filled
circles, with a dotted (men) and a dashed (women) regression line and a Rho/P text box. Every panel
is read from the page rendered at 1500 dpi, the tick labels included, by code shared in
`figures/_fig2.py`. That code was started by an earlier pass that could not render pages; this pass
rendered the pages and finished and checked it.

- **Calibration**: the axes are found as the longest ink runs. The long ticks (those that carry
  labels) are matched to the printed labels, and a straight line is fitted per axis.
- **Markers**: the circle radius is taken from the round holes inside isolated open circles.
- **Filled circles**: ink at least 0.75 R from paper.
- **Open circles**: a greedy search for rings that are almost wholly ink (at least 85% of each
  ring) and whose inside is not mostly ink. Each ring found then no longer counts towards the next.
  The inside limit is 0.7: a cluster of three overlapping men in panel D needed it, after the
  first try at 0.35 missed them.
- **Excluded**: the text box.
- **Intervals**: each point gets +/- (2 px + the panel's worst calibration misfit).
- **Overlays**: every overlay was checked by eye. Each circle has one cross, and none sits on a
  line, a letter or a marker of the other group.

- **Fig. 2(A)**, cardiomyocyte width against BSA: `fig2a_men` (46 open circles) and `fig2a_women`
  (11 filled). Calibration misfit 4.2 px (axis about 1650 px), intervals +/- 0.08 um.
- **Fig. 2(B)**, diffusion radius against BSA: `fig2b_men` (45) and `fig2b_women` (11). Misfit
  2.9 px, intervals +/- 0.03 um.
- **Fig. 2(C)**, capillary length density against BSA: `fig2c_men` (45) and `fig2c_women` (11).
  Misfit 2.7 px, intervals +/- 5 mm/mm3.
- **Fig. 2(D)**, diffusion radius against cardiomyocyte width: `fig2d_men` (45) and `fig2d_women`
  (11). Misfit 3.6 px, intervals +/- 0.04 um. It contains a cluster of three overlapping men at
  about (22.6, 17.6 um) under a filled circle, and two men drawn about 7 px apart at (23.5,
  13.7 um). Both were found and checked on a zoomed overlay.

## What the readings settle

- **Counts**: 46/45/45/45 men and 11 women in each panel, as stated. The legend's n=46 applies to
  panel A only, which agrees with the Table 2 footnote (q_fig2_legend_n).
- **Medians and quartiles** (model `fig2_group_stats`, runs `run_fig2_stats_m` and
  `run_fig2_stats_f`): width, radius (from panel B and from panel D), length density and BSA all
  reproduce Table 1/2, with three exceptions.
  - The men's median length density reads 1222 against 1226.
  - Its upper quartile reads 1546-1550 against 1555 (q_fig2_lv_men_median).
  - The women's upper quartile depends on the percentile definition; the Hazen definition gives
    the printed 1484 exactly (q_fig2_percentile_method).
- **Medians of per-patient ratios**: radius/width, radius/BSA and width/BSA reproduce the printed
  0.67/0.78, 8.0/9.0 and 11/12. This settles the open question q_ratio_of_medians: the printed
  ratios are medians of per-patient ratios (q_fig2_settles_ratio_of_medians).
- **Spearman coefficients (men)**: 0.302, 0.375, -0.371 and 0.387 against the printed 0.30, 0.37,
  -0.37 and 0.39, all reproduced (with tied BSA given average ranks: q_fig2_ties).
- **Per patient** (model `radius_per_patient`, built from `diffusion_radius`): each patient's
  sqrt(1/(pi Lv)) from panel C is compared with the same patient's radius in panel B.
  - Women: all reproduced or close.
  - Men: every plotted radius is 0.03-0.16 um below the formula (mean 0.08 um, about 0.5%), and
    16 of the 45 are not reproduced. This is a finding, not a reading error: q_fig2_radius_offset.
- **Not compared point by point**: panel D's points against panels A and B. Pairing D's (width,
  radius) points with A's widths and B's radii through BSA would need a width-radius assignment
  within tied BSA groups that uses the values being checked. D's radii are compared instead
  through their median and quartiles (`cmp_fig2_RD_*`, all reproduced) and their per-patient
  radius/width median. The validator's warning that `fig2d_radius_m`/`_f` are never compared on
  their own refers to this.
- **Not read**: the regression lines. They are drawn fits to the same points and no value is
  printed for them.
