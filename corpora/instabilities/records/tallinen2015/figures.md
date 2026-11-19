# Figures in tallinen2015

All plots in this paper are vector graphics; every panel with values was rendered at 1200 dpi (Fig. 1(b),
(c): 1800 dpi) and read by code in `figures/`. The shared code is `figures/_tal.py` (calibration, line
choice, markers, vertical lines, intervals; its docstring gives the rules); each reading's file names its
curve and the tick labels matched. Calibration is from tick marks found in the image and matched in order
to the printed labels; the largest misfit of the fitted axis is reported per reading (0.0-0.3 px for
Figs. 1, 2 and 4; 1.2 px in x and 0.7-1.7 px in y for the MATLAB frames of Fig. 3). Every reading was
checked with `boxgraph figure check`; the magenta marks sit on the curves, points and lines meant
(zoomed contact sheets in `figwork/zoom_fig*.png`).

The figure tools were refused in the earlier pass (`q_figures_not_read`); this pass reads the figures that
question lists.

## Fig. 1 (p. 2): Eq. 1 and its first unstable mode

- **Fig. 1(a)**: read `fig1a_eta2`, `fig1a_eta1`, `fig1a_eta06`, `fig1a_eta04`: the solid lines for
  eta = 2, 1, 0.6 and 0.4 (chosen by their order from the bottom at l/a >= 1.5, where the lines are apart),
  at l/a = 1.5-5.8. Ticks: x every 1 (0 at the y axis), y long ticks every 0.5; misfit 0.2 px. Compared
  with `eq1_threshold` swept over l/a (`cmp_fig1a_*`). Left out: the lines for eta = 0, 0.1, 0.2, 0.3
  (they leave the plot through the top within a short range of l/a and crowd near l/a < 1.5), 0.8 and
  1.5 (read lines already bracket them), and the dashed eta_b line (its value is the Biot threshold,
  compared elsewhere).
- **Fig. 1(b)**: read `fig1b_mode` (solid line, l/a of the first unstable mode, eta = 0.7-4.8) and
  `fig1b_asym` (dashed stiff-layer asymptote; between dashes a local quadratic fit to the dash centres,
  which widens the interval). Misfit 0.2 px. Compared with `first_unstable_mode` and
  `stiff_wavelength_asymptote`.
- **Fig. 1(c)**: read `fig1c_threshold` (solid line, including the flat gb part at eta = 0.2, 0.4) and
  `fig1c_asym` (dashed asymptote, eta >= 1: near eta = 0.7 the dashes are steep and their slanted ends
  bias a reading). Misfit 0.2 px. Compared with `first_unstable_mode` and
  `stiff_threshold_asymptote`. The black dotted guide lines at eta_b, eta_s and gs mark printed values
  that are compared in the record already; not read.

## Fig. 2 (p. 3): folding in two dimensions

- **Fig. 2(a)**: read `fig2a_linear` (solid blue linear-instability threshold, eta = 1.5-9.8) and
  `fig2a_linear_dotted` (its dotted part below eta_s, eta = 0.2-1.0), compared with
  `first_unstable_mode`; and `fig2a_cusp`, the ten black finite-element points for cusp formation
  (marker cores in a black-or-blue mask; the point at eta = 10 is cut by the frame and not read).
  Misfit 0.3 px. The cusp thresholds come from the finite-element code (`fe_folding`, not runnable) and
  have no comparison; the first point sits at the printed (eta_s, gs). The blue curve lies slightly below
  Eq. 1 between eta_b and about eta = 2 (`q_fig2a_curve_low`).
- **Fig. 2(b)**: read `fig2b_linear` (solid blue wavelength of linear instability, g = 1.15-1.5; not read
  where markers of other colours cover it) and `fig2b_linear_dotted` (its dotted end above gs), compared
  with `wavelength_at_threshold` (h = a/gz as printed) and its variant `wavelength_at_threshold_gza`
  (h = gz a). This curve settles `q_h_relation`: the h = gz a variant reproduces it and the printed
  relation does not (`q_fig2b_h_relation`). Read as finite-element
  points: `fig2b_eta8`, `fig2b_eta4`, `fig2b_eta2`, `fig2b_eta1`, `fig2b_eta05`, `fig2b_eta0` (marker cores
  per colour; hollow circles filled first). Misfit 0.2 px. Points partly hidden behind circles of another
  colour are read with a widened interval; points with no visible core are not read: the cyan eta = 2
  circles at g >= 1.7 under the red eta = 1 circles, the hollow cyan circle at g ≈ 1.37 crossed by the
  blue line, the red eta = 1 circles at g >= 2.0 under the blue ones, and every circle cut by the right
  frame at g = 2.4.
- **Fig. 2(c)-(e)**: left out: simulated configurations (stress maps), a micrograph of a ferret brain and
  images of chick gut; no axes or values.

## Fig. 3 (p. 3): hysteresis loops

- **Fig. 3(a)-(c)**: read `fig3a_loop`, `fig3b_loop`, `fig3c_loop` (the blue finite-element amplitude A/h
  against g, eta = 0.5, 1, 4); no model in the record produces them. Read the dashed vertical threshold
  lines as g values at A/h = 0.1: `fig3a_sulc`, `fig3b_sulc` (Sulcification, gs), compared with
  `sulcification_line` (g = 1/lambda_s); `fig3a_lin`, `fig3b_lin`, `fig3c_lin` (Linear instability),
  compared with `threshold_line` (g_c(eta) from Eq. 1). Ticks matched to the labels inside the frame;
  misfit 1.2 px (x), 0.7-1.7 px (y). The short dashed U = Uref line of (b), the red and blue arrows and
  their words are not data.

## Fig. 4 (p. 4): folding in three dimensions

- **Fig. 4(a), (f), (g), (h)**: left out: pattern images and photographs.
- **Fig. 4(b)**: read `fig4b_threshold` (the blue threshold curve where it falls with eta, eta = 1.5-9;
  not at eta = 3, 6, 10 where the blue "o" symbols cut it), compared with `threshold_equibiaxial`
  (g^(3/2) = g_c(g eta)), and `fig4b_sulc` (its flat part at eta = 0.2-0.6), compared with
  `sulcification_line_biax` (g = (1/lambda_s)^(2/3)). Misfit 0.3 px. Left out: the pattern symbols (Y, Z,
  o, line-like sulci) mark a category at each simulated grid point, not a value; the dotted contours of
  epsilon/epsilon_c are drawn from the threshold curve and are not separate results.
- **Fig. 4(c)**: left out: for each eta the triple-junction (solid) and zigzag (dashed) energies are drawn
  with circles that overlap within a marker diameter at every strain, and which circle belongs to which
  series cannot be told from the image.
- **Fig. 4(d)**: read `fig4d_linear` (thick black wavelength of linear instability), compared with
  `wavelength_at_threshold_biax` and `_gza` (see `q_fig4_black_curve`), and the finite-element zigzag
  half-wavelengths per colour and series: `fig4d_eta10_ly`, `fig4d_eta10_lx`, `fig4d_eta6_ly`,
  `fig4d_eta6_lx`, `fig4d_eta3_ly`, `fig4d_eta3_lx`, `fig4d_eta086_ly`, `fig4d_eta086_lx`. The l_y/2
  (solid) and l_x/2 (dashed) points of one colour share g values; they are told apart by height (l_y/2 the
  upper, except for eta = 0.86 at g = 2.0 where the dashed line ends above the solid one); the single
  eta = 0.86 point at g = 1.67 is kept in both. Misfit 0.2 px.
- **Fig. 4(e)**: read `fig4e_linear` (thick black curve, as in (d)) and the triple-junction
  half-wavelengths `fig4e_eta10`, `fig4e_eta6`, `fig4e_eta3`, `fig4e_eta086`. Misfit 0.2 px.

The finite-element points and loops (Figs. 2(a) black, 2(b), 3, 4(d), 4(e)) have no comparison: the
record's finite-element model is not runnable (`q_fe_results`). They are recorded for later papers'
models.
