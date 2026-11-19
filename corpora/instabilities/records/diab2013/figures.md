# Figures of diab2013

The first reading pass digitized no figure (the figure tools were not available to it). This pass
(2026-11-18) reads every panel that plots values, with calibrated code readings (`figures.yaml`,
`figures/*.py`). The figures are bitmaps embedded in the PDF; at 1200-1500 dpi their lines are blurred
over a few pixels but clean. All readings share `figures/_diab.py`: each axis is calibrated from the
tick marks found in the image, matched one to one to the printed tick labels and fitted (the misfit
below is the largest tick residual, in pixels at the reading's dpi); the ink is opened with a square
a little smaller than the plotted lines, which removes the thin dotted and dash-dot guide lines,
hairline arrows and asterisks; a curve is then followed column by column from a stroke picked at a
start position (or, for dotted lines and steep dashes, its pieces are selected by position and size),
and each value is a local line fit. Each 95% interval is half the line thickness along the y axis,
plus both calibration misfits (the x misfit through the local slope), plus twice the fit's rms.
Every reading was checked on its overlay (`figwork/<id>.png`).

- **Figure 1 (p. 3)**: schematic of the ruga phases; a drawing, nothing to read.
- **Figure 2a (p. 6)**: read.
  - `fig2a_bifurcation`: the bifurcation curve (solid below M, dashed above), eps = 0.02-0.40; x misfit
    1.4 px, y 1.3 px (10 kbar = 2305 px). Swept through Eq. 2.8 (`run_eq28_fig2a`, `cmp_eq28_fig2a`):
    the plotted curve agrees with Eq. 2.8 at every position read (e.g. 0.4165 vs 0.420 at eps = 0.1,
    2.702 vs 2.685 at 0.36, 4.69 vs 4.64 at 0.40). Beyond 0.40 the curve is nearly vertical (kbar is
    ill-conditioned in eps) and the follower leaves the dashes, so it is not read there.
  - `fig2a_lower_bound`: the chain curve (FEM lower bound of the crease strain), eps = 0.28-0.335; same
    calibration. Its dots are dropped and its dashes taken as pieces lying wholly above the bifurcation
    curve; above eps = 0.32 it is steep and its intervals are wide. No runnable model (FEM,
    q_fem_not_runnable). Its asymptote eps_H is printed in the text (0.35, recorded).
- **Figure 2b (p. 6)**: read, `fig2b_energy`, eps = 0.02-0.42, in the axis's own units (labelled
  delta phi^b / zeta^4 x 10^-3); x misfit 1.7 px, y 1.3 px. The readings change sign between eps = 0.25
  (+0.13) and 0.30 (-0.16), bracketing the printed eps_M = 0.272, and stay negative to the curve's end
  at about eps = 0.44, short of B (the curve is not drawn back to zero at eps_B). Not compared: the
  normalization is unstated (q_fig2b_normalization) and the record's energy-variation models output
  only the M-point.
- **Figure 3 (p. 9)**: FEM meshes and strain contour plots; pictures, no values to read.
- **Figure 4a-c (p. 10)**: read, the Fourier coefficients of the FEM surface profile (log10 y axes).
  - `fig4a_A1`, `fig4b_A1`, `fig4c_A1`: the solid line A1, each up to its eps_c; misfits (x, y) 2.1/3.0,
    1.2/1.5 and 1.2/2.2 px (one decade is about 190 px).
  - `fig4a_A2` (eps 0.16-0.185), `fig4b_A2` (0.25-0.27), `fig4c_A2` (0.30-0.35): the dashed line A2,
    only where it runs clear of the others (in (a) after its rise past eps_w, in (b) after it crosses
    the dotted A4 near 0.235).
  - Left out: A2 in (a) below 0.155 and in (b) below 0.25, and every A4 (dotted) and A8 (chained) line:
    at the levels 10^-7-10^-5 these lines and A2 cross and touch within a line width, and the dotted and
    chained lines are broken into dots that cannot be assigned to one line where they meet. In (a) above
    0.16 A4 and A8 are separate and could be read with a dot-following reading; not done in this pass.
  - The vertical dotted lines eps_w(i), eps_c(i), eps_c(ii), eps_c(iii) mark strains whose values are
    not printed (except eps_w(i) = 0.157, recorded); their positions were not read (a vertical line is
    not a y(x) reading). eps_c(iii) (about 0.35 by eye) against Eq. 2.8 at kbar = 2.51 would test the
    paper's statement that C13 is the instantaneous-crease curve.
  - No runnable model: FEM (q_fem_not_runnable).
- **Figure 4d (p. 10)**: read, `fig4d_i` (eps 0.01-0.15, up to the peak at eps_w(i)), `fig4d_ii` (0.01-0.26),
  `fig4d_iii` (0.01-0.34): the growth rate dA1/deps of the three cases, each the top, middle and bottom
  line where they run side by side; misfit x 1.6 px, y 1.0 px. Not read: the short branch of (i) between
  its peak and eps_c(i), and the vertical rises at creasing. FEM, no model.
- **Figure 5 (p. 11), main panel**: read; x misfit 1.1 px, y 2.2 px (1 kbar = 1110 px).
  - `fig5_C12_C13`: the solid curves C12/C13 (with the FEM dashed line superposed on C13), eps = 0.02-0.36.
    Swept through Eq. 2.8 (`run_eq28_fig5`, `cmp_eq28_fig5`): agrees to the third digit (e.g. 0.7267 vs
    0.727 at 0.18, 2.207 vs 2.199 at 0.34).
  - `fig5_C2c_lower`: the setback-crease curve C2c from T towards R, eps = 0.20-0.55 (0.325 at 0.20 down
    to 0.115 at 0.55).
  - `fig5_C2c_upper`: C2c from T up to M, eps = 0.185-0.22 (steep dashes taken as pieces below C12);
    above 0.22 the dashes merge with C12 and are not read.
  - The T-, M- and R-points and the dash-dot guide lines are printed in the text and recorded there.
- **Figure 5 (p. 11), inset**: read at 1500 dpi; x misfit 2.4 px, y 1.6 px (0.01 kbar = 518 px).
  - `fig5i_C4c`: the dashed fold-crease curve C4c, eps = 0.585-0.695 (0.1087 at 0.585, 0.0894 at 0.695);
    not read at 0.595 (the R asterisk) or 0.62 (the (f) asterisk).
  - `fig5i_C24`: the dotted folding curve C24, eps = 0.60-0.625, from 20 dots below the (e) asterisk.
  - Bearing on q_fold_strain_060: C24 runs from about eps = 0.598 (at the (e) point, kbar = 0.104) to the
    right as kbar falls (0.102 at 0.60, 0.091 at 0.62), so every fold below the R-point needs an applied
    strain above about 0.60, while the R-point itself is printed at 0.593. The figure is consistent with
    both printed statements: 0.593 is where C2c, C24 and C4c meet, "more than 0.60" is the strain along
    C24 for kbar below it. It does not explain the bound kbar < 0.15 of p. 11.
- **Figure 6 (p. 12)**: read four of six curves; x misfit 1.9 px, y 1.9 px. Line styles were matched to
  the legend by dash pattern and by where each curve rises vertically (2.510 at about 0.355, the
  Eq. 2.8 bifurcation strain of kbar = 2.51; 0.204 at about 0.31).
  - `fig6_k0100`: the coarse-dotted line (kbar = 0.100), eps = 0.10-0.55, from 80 dots below the
    45-degree line.
  - `fig6_k1300`: the solid line (kbar = 1.300), eps = 0.03-0.26, on the 45-degree line up to eps_M.
  - `fig6_k0204`: the short-dashed line (kbar = 0.204), eps = 0.21-0.29.
  - `fig6_k2510`: the chained line (kbar = 2.510), eps = 0.29-0.345.
  - Left out: the long-dashed (0.628) and double-chained (0.314) lines, which are nearly vertical
    between eps = 0.15 and 0.21 (eps_l is ill-conditioned in eps there) and cross each other and the
    chained 2.510 line; and every curve below eps = 0.2 where the dashed, chained and solid lines lie on
    or within a line width of the 45-degree line. The ends of the curves at eps_l = eps_B (the printed
    crease-tip result) are vertical and not read as y(x).
  - FEM, no runnable model.
