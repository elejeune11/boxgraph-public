# wang2015: figures

Every reading is `mode: code` (the code is in `figures/`). The build renders the crop and reruns the
code. Each overlay was checked with `boxgraph figure check` (images in `figwork/`, not committed).
Calibration misfit is the largest residual of the straight-line axis fit, in pixels of the crop.

- **Fig. 1** (p. 2): photographs, schematics and an energy sketch. Left out: no values.
- **Fig. 2** (p. 3): the 3D phase diagram as a perspective drawing. Left out: no axis can be
  calibrated in a perspective view; its sections are Figs. 3A and 4.
- **Fig. 3A** (p. 4), 750 dpi. Calibrated by `boxgraph.digitize.find_axes`: eM from the y-axis line
  (0) and six ticks (0.1 ... 0.6); mu_f/mu_s from the frame edges (10^-1, 10^5) and the decade ticks
  10^0 ... 10^3 snapped from the frame. Misfit 0.5 px on both axes.
  - `fig3a_theory`: the solid "Theory" curve (Eq. 4), read as eM at mu_f/mu_s = 1.5 ... 100. Above
    about 200 the curve runs into the left frame's tick marks and cannot be read. It is compared with
    `eq4_wrinkle_onset` (`cmp_eq4_fig3a`, reproduction). It agrees within 3% on both branches.
  - `fig3a_fe_fold_pd`, `fig3a_fe_pd_ridge`, `fig3a_fe_crease_fold`: the horizontal dotted
    finite-element boundaries. Fold/period-double reads 12.0-12.2 (printed ≈ 12), period-double/ridge
    about 806 (printed ≈ 800), and crease/fold right of the triple point 1.31 (printed 1.3).
  - `fig3a_fe_flat_crease`: the vertical dotted line of Eq. 3, eM = 0.350 at every ratio read.
  - `fig3a_fe_wrinkle_fold`, `fig3a_fe_wrinkle_pd`, `fig3a_fe_wrinkle_ridge`: the dotted boundary
    between wrinkle and the advanced modes, eM = 0.31-0.33. The wrinkle/period-double line reaches
    0.324 at mu_f/mu_s = 400, a little above the printed region "0.3 < eM < 0.32"
    (`q_fig3a_lines_read`).
  - These finite element lines have no runnable model (`q_fe_not_runnable`). They are recorded as
    predicted data for the relation jobs, e.g. against the period-doubling and ridge thresholds of
    cao2012 and wang2014.
  - Left out: the experimental markers (+, stars, triangles, crosses, diamonds, squares). Each one
    places a categorical observation (which pattern was seen) at a set mismatch strain and modulus
    ratio, and the reading has no value to return beyond the experiment's set conditions. The
    observed onsets the text prints from them are already data (`crease_onset_measured`, ...).
- **Fig. 3B-E** (p. 4): photographs labelled with eM. Left out: no plotted values; the text prints
  the onsets.
- **Fig. 4A-F** (p. 6), 1000 dpi, readings `fig4a_delam` ... `fig4f_delam`: the red boundary of the
  delaminated-buckle region at Gamma/(mu_s H_f) = 0.13, 0.28, 0.46, 0.81, 3.99 and 66.63. Each is read
  as mu_f/mu_s at given eM (code `_fig4.py`). The raster is blurred and the frame is not black, so
  lines are found by local contrast. Calibration uses the frame edges (0, 0.6; 10^-1, 10^5) and the
  major ticks on the bottom and right edges: 5 + 5 matched in every panel, misfit 1.9-2.4 px (x) and
  1.2-1.6 px (y). Columns where the curve meets other red marks (the inset photographs' arrows, marker
  circles) are not read. Finite element results, not runnable: recorded for the relation jobs
  (wang2014's delamination boundaries).
  - Left out: the circle markers, which are categorical observations as in Fig. 3A. Also left out are
    the black boundaries between the non-delaminated modes, which repeat those of Fig. 3A at lower
    adhesion.
- **Fig. 5A** (p. 7), 900 dpi. The frame's inward ticks are matched to 0.4 ... 1 on both axes; misfit
  2.0 px (x) and 3.7 px (y).
  - `fig5a_theory`: the "Theory" line, identical to Eqs. 9-12 within 0.2% (`cmp_accordion_fig5a_line`).
  - Measured, with error bars (unstated what they are), one seed per marker (see `_fig5.py`):
    - `fig5a_wrinkle`: 9 wrinkle points. Three in the cluster at x ≈ 0.9 overlap and get the whole
      marker as their interval.
    - `fig5a_fold`: 10 fold points. Two overlap at x ≈ 0.69, one is half hidden at 0.81 and one hidden
      at 0.91.
    - `fig5a_pd`: 7 half-period-double points.
    - `fig5a_ridge`: 6 ridge points.
  - Each series is compared with `accordion_eqs9_12` (`val_accordion_fig5a_*`). A seventh ridge square
    may lie behind the markers at x ≈ 0.81; it cannot be told apart and is not read. Folds lie 4-12%
    above the line and ridges 7-14% below it (`q_fig5a_series_offsets`).
- **Fig. 5B** (p. 7), 900 dpi. Ticks 0.6 ... 1 and 0 ... 0.2 (all on the frame edges); misfit 1.2 px
  (x) and 1.6 px (y).
  - `fig5b_theory`: the "Theory" curve, identical to Eq. 13 within 0.4% (`cmp_eq13_fig5b_curve`). It
    confirms the spot values 0.178, 0.167 and 0.138 that the earlier pass checked by eye.
  - Measured, with error bars: `fig5b_r3p6` (4 points), `fig5b_r9p8` (3), `fig5b_r14p8` (4) and
    `fig5b_r9110` (3), for mu_f/mu_s = 3.6, 9.8, 14.8 and 9110. Each is compared with
    `eq13_wrinkle_amplitude` (`val_eq13_fig5b_*`).
  - This settles `q_fig5b_10pct_claim`, in a new question, `q_fig5b_claim_read`. The 3.6 series lies
    10-15% below Eq. 13, beyond its error bars, which contradicts "match well for low modulus ratios".
    The 9110 points at 0.70 and 0.75 are 16-17% low, beyond the stated 10%.
- **Fig. 6A** (p. 7): the systems of Table 1 drawn as ellipses on the Fig. 3A diagram. Left out: the
  ellipses are drawings of the ranges in Table 1, which is recorded value by value. The boundaries
  repeat Fig. 3A.
- **Fig. 6B** (p. 7): the diagram stacked over eM = 0.1-0.4 against Gamma/(mu_s H_f). The grey band
  is the delamination transition smeared over that strain range, so it is not one curve. It projects
  the same finite element results that Fig. 4 sections, and Fig. 4's red curves are read. The
  ellipses are Table 1 again. Left out.

Earlier pass: no figure had been read (`q_figures_not_read`). Its eye-read data stay as they were;
no datum in the record was printed with "~" from a figure.
