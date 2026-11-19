# Figures of wang2014

Figure pass of 2026-11-18. All readings are `mode: code` at 1200 dpi; the code is in `figures/`
(shared pieces `_wang.py`, `_fig3.py`, `_fig6b.py`, `_fig7a.py`, `_fig13.py`, `_fig14b.py`, each with
its method in the docstring). Calibration in every panel: the plot frame is found from its own ink,
tick marks standing inward from the bottom and left frame lines are matched in order to the printed
labels (frame lines at the end labels), and a line (in log10 for log axes) is fitted; the largest
misfit is given below and added to every interval. Each reading was checked with
`boxgraph figure check` and its overlay inspected (`figwork/<reading id>.png`).

- **Fig. 1, 2, 4(a-f), 8(a-d), 9(a-c)**: schematics. Left out (drawings, no values).
- **Fig. 4(g-l), 5(e), 8(e-g), 9(d-e)**: micrographs. Left out (images; the strains printed on 5(e)
  are frame labels of one sample's propagation, not data).
- **Fig. 3** (measured adhesion energy against film modulus): read as `fig3_lp1` (blue circles),
  `fig3_lp2` (red triangles), `fig3_lp3` (green squares), with error bars (unstated what they are,
  `q_fig3_error_bars`). Markers found by template matching against the legend's own marker, caps of
  the error bars by colour beside the stem. Misfit 2.2 px. Green squares (drawn on top) all six read
  with both caps; red triangles six, interval widened by h/6 for the triangle's anchor; blue circles
  five (the one at about 155 kPa is wholly hidden), one upper cap hidden and mirrored. Bar midpoints
  agree with marker centres within about 0.03 N/m. No model predicts adhesion; data for later
  jobs (`adhesion_fig3_*`).
- **Fig. 5(a)**: finite-element contour plot. Left out (an image of a field).
- **Fig. 5(b), 5(c)**: finite-element energy curves against D/H_f for one case
  (Gamma/(mu_s H_f) = 0.44, mu_f/mu_s = 2). Left out: their only result, e_c buckle = 0.28 with
  D = 10.2 H_f, is printed and recorded; the curves are finite-element output that no model in the
  record can produce (`q_fe_not_runnable`).
- **Fig. 5(d)**: finite-element energy barrier against Gamma/(mu_s H_f), six curves. Left out for the
  same reason, and because the curves for mu_f/mu_s = 5, 8, 10 are crowded and partly
  indistinguishable at this resolution.
- **Fig. 6(a)**: red line 'Wrinkling' read as `fig6a_wrinkle` (11 positions, mu_f/mu_s 1.5 to 9.75),
  misfit 3.4 px (the 0.35 tick is hidden under the dashed crease line and not used). Compared with
  `wrinkle_linear_stability` by a sweep (`cmp_wrinkle_fig6a`, reproduction). The dashed crease line
  is the printed constant 0.35 (`eps_crease`). The blue finite-element delamination curves
  (Gamma/(mu_s H_f) = 0.1 to 1) are left out: finite-element output, not rerunnable.
- **Fig. 6(b)**: red circles (delamination/wrinkling boundary) `fig6b_delam_wrinkle` and blue squares
  (delamination/creasing boundary) `fig6b_delam_crease`; misfit 2.1 px; hollow markers filled and
  separated from the joining line by an opening, centres at distance-transform peaks. The red circle
  at the triple point is hidden by the blue square and black line (the point is printed as
  (0.77, 1.54)). Finite-element results (`q_fe_figure_readings`); the black wrinkling/creasing line at
  1.54 is the printed `mu_b_lp1`.
- **Fig. 7(a)** (lambda_p = 2, log x): experimental modes read as `fig7a_exp_wrinkling` (5 stars),
  `fig7a_exp_creasing` (9 diamonds, one partly under the word 'Creasing'), `fig7a_exp_delamination`
  (15 triangles, overlapping pairs separated); template matching against the legend markers; misfit
  2.5 px. Blue boundary squares `fig7a_delam_crease` (7; the last is under the triple-point circle).
  The near-vertical red delamination/wrinkling line is left out: it is a thick line whose three small
  circles cannot be told from it, and a near-vertical line cannot be read as y against x. These
  readings settle `q_experiments_on_diagram`: see `q_fig7a_experiments_read` (experiments put the
  wrinkling/creasing boundary between about 1.84 and 3.8, above the calculated 1.22).
- **Fig. 7(b)** (lambda_p = 3): blue squares `fig7b_delam_crease` (4), misfit 3.6 px. Red
  near-vertical line left out as in 7(a).
- **Fig. 10(a)**: finite-element contour plot. Left out.
- **Fig. 10(b)**: finite-element energy curves for one case; left out as 5(b, c) (its crossing is
  marked, not labelled).
- **Fig. 10(c)**: blue line read as `fig10c_wrinkle_buckle` (Gamma/(mu_s H_f) 0.65 to 1.18), misfit
  3.4 px; finite-element result, not rerunnable. The red dashed line is e_c wrinkle at
  mu_f/mu_s = 10, lambda_p = 1, already checked through Figs. 6(a) and 14(b) at that ratio; not read
  separately.
- **Fig. 11(a-c)**: finite-element energy differences for single cases, each a short segment between
  two marked strains with no labelled values. Left out (finite-element output; no model).
- **Fig. 12(a, b)**: advanced-mode phase diagrams from finite-element energies; their labelled corner
  points are recorded as printed (`adv_*`). The boundary lines are left out: finite-element output
  with no model in the record (`q_adv_points_fe`); the boundaries are steep or vertical lines with
  small markers that would need reading as x against y.
- **Fig. 13(a-d)** (measured nominal stress against stretch of 2-5% Sylgard): red bands of measured
  points read as `fig13a_test` ... `fig13d_test`; the band is traced with the red mask closed
  vertically across the blue fit line, value at the band centre; misfit 1.2-2.6 px. Compared with
  the neo-Hookean law at the printed moduli (`neo_hookean_uniaxial`, `cmp_neo_fig13*`, fit_quality);
  the paper says the law holds below a stretch of 2.2, and panels (b) and (d) are read beyond it.
  The blue fit lines themselves are not read (they are the model).
- **Fig. 14(a)**: finite-element energy of the wrinkled state for one case; its crossing (the
  critical strain) is marked but not labelled. Left out (finite-element output).
- **Fig. 14(b)**: read `fig14b_lp1` (solid red), `fig14b_lp1p5` (dashed blue) and `fig14b_lp3`
  (magenta with crosses) at mu_f/mu_s 1.05 to 90; misfit 3.2 px. The orange dotted (lambda_p = 2) and
  green dash-dot (2.5) lines are interleaved with each other and the others over most of the range
  and are left out. Each is compared with `wrinkle_linear_stability` at its prestretch
  (`cmp_wrinkle_fig14b_*`). This tests `q_boundary_prestretch` directly: see
  `q_fig14b_prestretch_curves` (the paper's plotted lambda_p > 1 curves are consistent with its printed
  boundaries but differ from the recorded model).
