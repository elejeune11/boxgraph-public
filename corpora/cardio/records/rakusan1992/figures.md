# Figures of rakusan1992

- **Fig. 1** (p. 4): drawings of capillary positions and domains in four fields. No values to read;
  the four field densities the legend prints (3,040, 3,306, 2,052, 1,406 per mm^2) are single fields
  and feed no model, so they are left out.
- **Fig. 2** (p. 5), capillary density against heart mass, one marker per heart; rendered at 900 dpi
  (crop [840, 960, 3480, 2830], plot box about 2290 x 1670 px). Read with the shared code
  `figures/_scatter.py`. Calibration from the image: the frame's spines, the inward tick marks on all
  four spines matched to the printed labels (x 200-1000 g, y 1500-4500 /mm^2), each axis fitted as a
  plane to absorb the slight rotation of the scan; largest tick misfit 2.3 px (x) and 2.5 px (y),
  about 1.2 g and 6 /mm^2.
  - `fig2_fit`: the thick middle line (the fitted cubic), not the two thin lines either side (the
    legend does not say what those are; they look like a confidence band and are not read). Traced on
    the ink opened with a 5 px disc (removes the 9-11 px thin lines and open markers, keeps the
    14-18 px thick line) from seven seeds; where the line passes under a filled marker it is
    interpolated and the interval covers the marker. Read at 50-850 g every 50 g and at 875 g (the line
    ends under a marker at about 905 g). The printed cubic reproduces it at every x
    (`cmp_cdpoly_fig2_fit`).
  - `fig2_acquired`: filled circles found as solid ink (opening with a disc of 0.3 of the legend
    marker's diameter), each blob counted by its area against the legend marker; three blobs of two
    overlapping discs were split. All 13 hearts of Table 4 found. Their means reproduce Table 4's
    density (1671 ± 66) and heart mass (634 ± 49).
  - `fig2_normal`, `fig2_congenital`, `fig2_coarctation`: open circles, squares and triangles found by
    normalized cross-correlation with the legend symbols, with a check that the outline is complete.
    Found 19 of 24 normal hearts (the rest overlap in the cluster at 20-60 g and near 180-250 g),
    19 of 20 congenital stenosis hearts, 4 of 5 coarctation hearts (the fifth triangle, near 425 g, is
    hidden behind a filled circle and the fitted line). Each marker centre +-3 px plus the misfit.
    These groups pool infants, children and adults, so their table means (by age) are not checked
    from the figure; the congenital and coarctation markers are run through the cubic for the
    paper's "lie above the line" claim, without a verdict (an inequality).
- **Fig. 3** (p. 5), capillary domain area against heart mass; rendered at 900 dpi (crop
  [840, 5750, 3480, 8090], which includes the legend below the plot; plot box about 2300 x 1650 px).
  Same code and calibration (ticks y 200-800 um^2); misfit 1.6 px (x) and 2.1 px (y), about 0.8 g and
  1.4 um^2.
  - `fig3_fit`: the thick line read at 100-850 g every 50 g and at 875 g (markers crowd the line below
    100 g). It rises to a plateau of about 633 um^2; the printed quadratic falls after 440 g. The
    comparison `cmp_dapoly_fig3_fit` is reproduced only within the rounding of the printed x^2
    coefficient "-0.001" (the drawn line needs about -0.0005): this answers `q_dapoly_coefficient`
    (see `q_fig3_drawn_curve`) - the coefficient was printed with too few decimals, not as a wrong digit.
  - `fig3_acquired`: all 13 filled circles (one pair of overlapping discs split). Their means reproduce
    Table 4's domain area (611 ± 26) and heart mass. Each heart's 1/density from Fig. 2 agrees with its
    domain area in Fig. 3 (`cmp_domain_per_heart_acq`, hearts paired by heart mass) within about 1-2%.
  - `fig3_normal` (19 of 24), `fig3_congenital` (18 of 20), `fig3_coarctation` (4 of 5): as in Fig. 2.
- The fits are compared with the individual normal and acquired-stenosis hearts as `fit_quality`
  (per heart; the scatter about the fit, r = 0.93 and 0.87, is large, so most hearts are not within
  the reading precision of the line - expected for a fit, not a finding).
- The figures and Tables 3-5 hold 62 hearts while the Methods say 63 (`q_heart_count`).
