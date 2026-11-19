# cao2011: figures

Every plot with values is read by the record's own code (`figures/*.py`, shared code in
`figures/_cao.py`), rendered from the PDF at 1200 dpi (Figs. 2-4, black line plots) or 900 dpi (Figs. 5-9,
coloured finite element markers). Calibration is from the image: the open L-shaped axes are the
longest neutral-ink runs; the major ticks are the longest strokes on each axis, kept only when evenly
spaced and as many as the printed labels; each axis is fitted to its majors (and the corner where it
carries a label). Misfits are the largest distance of a tick from the fit (printed in every value's
note). Curves are read as the dark runs crossing a column, chosen by order (from the top or bottom)
and thickness; markers are blobs of one colour, read at their box centre; a marker partly hidden by
another is placed from its visible edge; a row of overlapping markers is placed from its two outer
edges. Overlays: `figwork/<reading id>.png` (not committed); every reading was checked on its overlay.

All finite element (FE) values are the authors' ABAQUS results (origin `predicted`), not rerunnable.
There are no measurements in this paper.

- **Fig. 1 (p. 2)**: left out, a drawing of the coordinates, a wrinkle and a crease; no values.
- **Fig. 2(a) (p. 11)**: read. `fig2a_perfect_pos`, `fig2a_perfect_neg` (the two perfect lines),
  `fig2a_imperfect_outer_pos/neg` and `fig2a_imperfect_inner_pos/neg` (the two arms of each fold,
  lambda - lambda_W = 0.045 to 0.1). x: 6 marks, misfit 0.6 px; y: 5 marks, misfit 2.0 px (of 520 px per
  0.05). Compared with Eq. 4.8 (`two_mode_perfect_eq48`) and Eq. 4.7 (`two_mode_imperfect_eq47`, new) with
  the printed b112 and c and lambda_W^2 xibar_1 = +-0.0005 (added). **This settles q_fig2_caption_lambdaC**:
  the inner arms read 0.0051 at lambda - lambda_W = 0.1, which Eq. 4.7 gives for lambda_W^2 xibar_1 =
  0.0005 (0.0048) and not for the caption's lambda_C^2 xibar_1 = 0.0005 (0.0033); see the new question
  q_fig2_reading_lambdaW. Positions next to labels, leaders and the axis title were not read.
- **Fig. 2(b) (p. 11)**: read. `fig2b_perfect`, `fig2b_imperfect_outer`, `fig2b_imperfect_inner`; y: 7
  marks, misfit 2.9 px (of 350 px per 0.01). Same models; xi_2 = -b112 xi_1^2/[4(lambda - lambda_W)].
- **Fig. 3 (p. 12)**: read. `fig3_N2` (the outermost curve, at 25 positions where it is apart from the
  others), and the troughs at x1/l = 0.5 and 1.5 of N = 4, 6, 8, 10 (`fig3_N4_trough` ... nested, counted
  from the deepest). x: 5 marks, misfit 0.3 px; y: 6 marks, misfit 3.2 px (of 605 px per 0.5). N = 2, 4,
  6 are compared with the perfect N-mode solution of Eq. 4.6 (`nmode_perfect_shape`, new, the paper's
  continuation from N - 1). N = 8 and 10 have no model: Eq. 4.3 prints the b_ijm only up to mode 6.
  Elsewhere the N = 4-10 curves lie within a few line widths of one another and are not read.
- **Fig. 4 (p. 13)**: read. `fig4_N2` ... `fig4_N6` at lambda_W^2 xibar_1 = 0.001 to 0.0048 (at 0.0005 the
  curves merge; 0.0032-0.0036 is crossed by the label leader). x: 6 marks, misfit 0.6 px; y: 5 marks,
  misfit 2.8 px (of 795 px per 0.05). Compared with c*(N) sqrt(lambda_W^2 xibar_1)
  (`nmode_reduction_curve`, new, built on nmode_cstar_eq46). The readings (about +-0.2%) cannot decide
  q_table1_N5_N6: at 0.0048 both the printed c* (2.305, 2.358) and the computed (2.3098, 2.3618) fall
  inside the read intervals.
- **Fig. 5 (p. 16)**: read. `fig5_asymptotic` (the solid 6-mode line, traced from x = 0.026 because the
  label text lies above it on the left; x 0.009-0.014 is covered by arrows and markers),
  `fig5_eps_star_fe` (9 blue spheres; the first two overlap and are placed from their outer edges),
  `fig5_eps_A_fe` (9 dark red pentagons, the first two overlapping). x: 6 marks, misfit 0.0 px; y: 6 marks,
  misfit 0.4 px. The line is compared with eps* = 1 - lambda_W(1 + c* sqrt(xibar_1)), N = 6
  (`nmode_asymptotic_strain`, new); the FE eps* with the same line (approximation; see
  q_fig5_asymptotic_range); the FE eps_A with the stated criterion eps_A = eps_W = 0.456
  (`local_criterion_words`, consistency). The FE eps* at xibar_1 = 0.008 reads 0.349, just below eps_C =
  0.35, consistent with 'imperfections larger than about xibar_1 = 0.008' (p. 110). The inset is a
  drawing.
- **Fig. 6 (p. 17)**: read. `fig6_eps_fe` (dark red hexagons, eps) and `fig6_eps_A_fe` (blue spheres,
  eps_A) against Delta u2/l, xibar_1 = 0.005; legend markers (with text to their right) left out. x: 8
  marks, misfit 0.2 px; y: 6 marks, misfit 0.2 px. The hexagons at Delta u2/l = 0.0101, 0.0103 and 0.0106
  lie entirely behind spheres and are not read; four more are placed from their visible lower edge. Near
  Delta u2/l = 0.0365 each colour has a row of overlapping markers: the two outer ones are read, a third
  between them is hidden. No model in the record produces these loading paths; the last eps_A (0.455)
  reaches eps_W where eps reaches its maximum (0.368), as the caption says. The inset is a drawing.
- **Fig. 7 (p. 18)**: read. `fig7_du2_fe`: 20 blue spheres, Delta u2/l against eps (same simulation as
  Fig. 6; the values agree with Fig. 6's eps column to the reading precision). x: 6 marks, misfit < 1
  px; y: the six majors 0.015-0.040 (the 0.010 tick is shortened by a marker). Insets (a), (b):
  colour maps of the deformed mesh, no values; left out.
- **Fig. 8 (p. 19)**: read. `fig8_lc00144` (13 dark red hexagons, l_C/l = 0.00144) and `fig8_lc00295`
  (blue spheres, l_C/l = 0.00295) against X/l_C. The colour-map inset is masked out. x: 9 marks, misfit
  0.3 px; y: 6 marks, misfit 0.0 px. Two blue spheres (X/l_C about 0.4 and 1.1) lie wholly behind
  hexagons and are not read. No model in the record; both series cross eps_C = 0.35 between X/l_C = 2.1 and
  2.4 (red 0.340 at 2.07, 0.367 at 2.38; blue 0.348 at 2.23, 0.368 at 2.49), consistent with 'X ~ 2.3 l_C'.
- **Fig. 9 (p. 19)**: read. `fig9_eps_star_fe` (9 dark red spheres) and `fig9_eps_A_fe` (9 green
  hexagons), exponential imperfection; legend markers left out. x: 7 marks, misfit 0.4 px; y: 7 marks,
  misfit 0.3 px. eps_A compared with eps_W = 0.456 (`local_criterion_words_exp`, consistency); eps* has
  no model (no asymptotic result is given for this imperfection). The inset is a drawing.
