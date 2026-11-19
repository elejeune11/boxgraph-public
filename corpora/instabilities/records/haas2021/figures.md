# Figures of haas2021

All readings are `mode: code`; each reading's code is in `figures/<id>.py`, with shared code in
`figures/_fig3.py`, `figures/_fig5g.py` and `figures/_fig5strain.py`. Each was checked with
`boxgraph figure check`, and the overlays (in `figwork/`, not committed) show every mark on its curve.
Every calibration fits the ticks matched to the printed labels by a straight line; misfits are below.

- **Fig. 1 (p. 2)**: micrographs of Drosophila and Volvox cross sections. Left out: no values.
- **Fig. 2 (p. 2)**: geometry drawings. Left out: no values.
- **Fig. 3(a) (p. 10)**: read `fig3a_asphi` (alphabar_sphi/alphabar_ss, medium blue) and `fig3a_aphiphi`
  (alpha_phiphi/alphabar_ss, light blue) at eta = -0.95 ... 0.95. The colour masks are sampled from the page,
  and the axes calibrated on the ticks crossing the axes (misfit at most 0.2 px). The first legend entry,
  alphabar_ss/alphabar_ss = 1, is a constant by definition and is not read. Compared with `coeff_ratios_fig3`
  (closed forms of Eqs. 58, 64): all 78 positions reproduced.
- **Fig. 3(a), inset**: read `fig3a_inset_abss` (alphabar_ss, unscaled) at eta = -0.8 ... 0.8, at 2400 dpi.
  Steep parts are read row by row. Compared with `coeffs_bar_eq64` (Eq. 64a): all 17 reproduced.
- **Fig. 3(b)**: read `fig3b_bss`, `fig3b_bsphi`, `fig3b_bphis` and `fig3b_bphiphi` (the four legend entries,
  dark red to pale pink). Positions where a curve is wholly hidden under another are left out of `at`. Misfit
  0.3 px. All reproduced against `coeff_ratios_fig3`.
- **Fig. 3(c)**: read `fig3c_gss`, `fig3c_gsphi` and `fig3c_gphiphi`. gamma_phiphi beyond eta = 0.82 is
  hidden under the legend text, and eta = 0.1, 0.15 under another curve. Misfit 0.2 px. All reproduced. This
  settles the eye reading in q_figures_not_read: gamma_ss/alphabar_ss = 1/12 and gamma_sphi/alphabar_ss = 1/24
  at eta = 0 (read 0.0833 and 0.0417).
- **Fig. 4 (p. 12)**: micrographs of Volvox and schematic step functions of kappa_s0 and f_s0, f_phi0. Left
  out: the schematic has no numbered axes (its values are the printed parameters).
- **Fig. 5(a), 5(d) (p. 13)**: shapes of the shell (midlines and transverse extent). Left out: closed,
  double-valued outlines with no axes or scale bar, and no model in the record produces them.
- **Fig. 5(b), 5(c)** (kappa_b = -2, w = 0.2) and **5(e), 5(f)** (kappa_b = -8.5, w = 0.5): read
  `fig5{b,c,e,f}_large` (blue solid, Eq. 63) and `fig5{b,c,e,f}_classical` (red dashed, Eq. 67) at
  s = 0.1 ... 2.9, at 3600 dpi. The steep jumps at s = 1.0 and 1.5 and the end spike at s = 3 are left out.
  Where the red dash lies over the blue line, the blue extent includes it. The x ticks (every 0.5 in s) are
  found in a window off the axis, because in (b) and (c) the curves run along the axis. Misfit at most 0.4 px
  on both axes. The vertical axis is drawn about 16 px (0.012 in s) from the s = 0 the ticks imply, and in
  (c), (f) the horizontal axis 5-8 px (about 0.03 in K_s) from K_s = 0. The readings use the ticks. No model
  in the record produces these curves (q_volvox_not_rerun, q_fig5_curves_not_compared), so they are recorded
  without a verdict. Also read: the grey band's edges, `fig5b_band_left/right` and `fig5e_band_left/right`
  (s at levels where no curve lies on the edge). Compared with the stated bend region s0 - w < s < s0
  (`bend_region_edges`, printed s0 = 1.5, w = 0.2 and 0.5): 1.300, 1.500, 1.000 and 1.500, all reproduced.
- **Fig. 5(g)**: the grey line |eta| = 1 is read as `fig5g_eta1_line` (k at d = 0.1 ... 2.0, where the labels
  do not break it): k = 8.530 [8.522, 8.537]. It is compared with `constriction_k_eq59` (Eq. 59 solved for k,
  with the added f_s0 = f_phi0 = 0.8) and reproduced. With the alternative f = 1 it would be at 13.3, so the
  figure settles the stretch choice of q_eta_label_location (q_fig5g_eta1_settles_stretch). All twelve curves
  have distinct flat colours and are read on their lower branch, at k = 2.5 ... up to short of each fold:
  `fig5g_large_w03 ... _w09` (blue solid, darker = smaller w) and `fig5g_classical_w03 ... _w09` (red dashed).
  Each is traced column by column, and k values where a curve is wholly hidden are left out. Calibration: 8 x
  ticks, 8 y ticks, misfit 0.2 px. Left out: below k = 2.5, where all twelve curves lie on one another, and
  the middle and upper branches of the S-shaped and looped curves (multi-valued in k). No model produces the
  curves (q_fig5_curves_not_compared).
- **Fig. 6(a) (p. 19)**: sketches of zeta(Z0) with no numbered axes. Left out.
- **Fig. 6(b)**: read `fig6b_upper`, the upper branch of the solid blue boundary of the volume-conservation
  region, at K0 h^2 = -1.2 ... 7.0. The axes are calibrated on the fraction labels -16/9, 0, 64/9 and
  -sqrt(omega), -1, 0, 1, sqrt(omega) as numbers (misfit 0.2 px). Where the red dashed (H0)^2 = K0 lies over
  the blue curve, the reading uses the uncovered stroke edge. Compared with `volume_conservation_region`
  (conditions stated in words): all 41 reproduced. The lower branch is the mirror image (the region is
  symmetric in H0 h) and is not read separately. The red dashed boundaries are the closed forms
  (H0)^2 = K0 and K0 h^2 = -16/9, so they are not read either.
