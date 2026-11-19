# Figures of jin2015

Figure pass of 2026-11-19. Every reading is by the record's own code (`figures/*.py`), run on a crop
rendered at 900 or 1200 dpi. Each axis is calibrated from the panel's own tick marks: the long ticks
carry the labels seen on the panel, and on log axes every minor tick is matched to k x 10^n and
included in a least-squares fit. Shared helpers are in `figures/_jin.py`. The misfit is the largest
distance of any tick from the fitted axis. Each value's 95% interval adds half the line thickness,
the local fit residual, the axis misfits and one pixel. Every reading was checked on its overlay
(`figwork/<id>.png`).

## Read

- **Fig. 2 (p. 2)**, e_c against L_wrinkle/Hf, uniaxial: `fig2_G2H10`, `fig2_G50H1`, `fig2_G50H100`,
  `fig2_G1000H100`, the four blue curves. All four are the same blue, so each is picked by its order
  from the bottom in a column where all four are apart, then followed. It is read only where it is
  apart from the others: the curves merge for L/Hf < 6, and the G_f/G_s=50, H_s/H_f=1 curve is not
  read beyond its crossing with the G_f/G_s=2 curve near L/Hf = 30. Axes from 20 x ticks and 18 y
  ticks; misfit 5.7 px (x) and 3.8 px (y) on a 3000 px wide plot. Each curve is compared with the new
  model `wrinkle_ec_uniaxial` (Eq. B7 at a fixed wavelength), swept over L/Hf.
- **Fig. 3(a) (p. 3)**, contours of e_m in the (H_s/H_f, G_f/G_s) plane: `fig3a_c001`, `c002`, `c005`,
  `c013`, `c025`, `c044`, the six black contours. Each contour is picked by its order from the bottom
  in a clean column and read as its connected component. On steep parts the line covers many rows of
  a column, and the interval spans all of them. The frame is grey on a coloured fill, so it is found
  with a lighter threshold. Misfit 2.6 px (x, 41 ticks) and 2.2 px (y, 26 ticks). Compared with the
  new model `em_contour_uniaxial`, swept over H_s/H_f, with the printed contour label (e_m^Uni) as
  its input. The `e_m^Uni = 0.44` contour is the boundary of equal critical strain. Its flat part reads
  1.648 [1.596, 1.703], the printed 1.65.
- **Fig. 3(b) (p. 3)**, contours of L^m_wrinkle/Hf = 5, 11, 16, 25, 40: `fig3b_L5` ... `fig3b_L40`, read
  in the same way (the 25 contour is thin and grey, so a lighter line threshold is used). This
  scanned panel is coarser, with misfit 5.0 px (x) and 3.4 px (y). Compared with the new model
  `Lm_contour`. The vertical part of the L = 5 contour (H_s/H_f between 0.25 and 0.4) is not read:
  there the line has no definite G_f/G_s. The flat part of the L = 5 contour (H_s/H_f >= 1) is a
  separate reading, `fig3b_L5_flat`, kept as data only, because the equations give no G_f/G_s with
  L_m/H_f = 5 there (`q_fig3b_L5_flat`).
- **Fig. 4(a) (p. 4)**: `fig4a_boundary`, the boundary curve; the y axis has ticks only at its labels
  (3, 5, 7, 10, 20, 40), so it is fitted to those 6 ticks, with misfit 1.9 px. Compared with the
  e_m^Uni = 0.44 contour model. Also read: `fig4a_subcritical` (10 open circles) and
  `fig4a_supercritical` (6 pluses), the bilayers the finite element simulations classify. The legend
  box is found from its own frame and its sample markers are left out. The plus at H_s/H_f = 4 sits on
  the bottom frame and is cut by it, so its centre is biased up by a few pixels. No model in the
  record classifies creases (`q_crease_fe`), so these are data only.
- **Fig. 5(a)-(f) (p. 5)**: `fig5a_em` ... `fig5f_em`, the e_m marked in each energy diagram, read on
  the strain axis (linear, 4 to 6 ticks, misfit 0.7 to 2.3 px). In (a) and (b) it is the centre of the
  green diamond. In (c)-(e) it is the left end of the green wrinkle branch, where the label e_m
  stands. In (f) it is where the green branch leaves the flat line: the red flat line is drawn over
  it, so the interval runs from the last column on its baseline to the first column one line
  thickness below. The x of each reading is the panel's printed G_f/G_s (`at`). Compared with the
  existing plane-strain model at the panel's H_s/H_f (runs `run_fig5*_em`; the audit's runs
  `run_em_pe_pointA-F` are kept). These readings settle `q_points_AF_diamonds`; see `q_fig5_branch_start`.
- **Fig. 5(g) (p. 5)**: `fig5g_boundary`, the boundary curve (misfit 4.7 px x, 5.1 px y; its flat
  part reads 1.648), compared like Fig. 4(a). The squares A-F are not read, because their coordinates
  are printed in the text (data `Gf_Gs_pointA` ... `Hs_Hf_pointF`).
- **Fig. 7(a)-(d) (p. 8)**: e_m and L^m/Hf against G_f/G_s (a, b) and H_s/H_f (c, d), uniaxial.
  `fig7{a,b,c,d}_{curve}` are the green, red, black and blue solid curves. Each is traced by colour
  with a local straight-line fit; the black curve is followed from its right end, past the labels.
  `fig7{a,b,c,d}_vk` are all the open blue circles (von Karman plate on a linear substrate, Ref. 58),
  found by ring correlation (radius 15 px). The circles are erased before the blue curve is traced.
  Axes from 25 to 41 ticks, misfit 1.7 to 3.1 px. Not read: the blue curve of (a) below
  G_f/G_s = 15, where it lies under the black one; the red curve of (d) below H_s/H_f = 0.5, where it
  lies on the green one. The solid curves are compared with `wrinkle_eigen_uniaxial` swept over the x
  read. The paper drew them as straight segments between computed points (visible kinks, e.g. at
  H_s/H_f = 4, 10 and 20 in (c), (d)), so values read between those points carry the segment's chord
  error. The circles are recorded as data from Ref. 58 (huang2005); no model here computes them.

## What the readings show

- Fig. 2 (four curves) and Fig. 7 (sixteen solid curves) are reproduced by Eqs. B7-B15 at every
  point read, except a few "close" points near the ends (Fig. 7(b) H_s/H_f = 1000 at
  G_f/G_s < 4; Fig. 7(d) at H_s/H_f = 0.12).
- Fig. 3(a): the contours e_m^Uni = 0.01 to 0.13 are reproduced. The 0.25 contour is close on its
  flat part. The 0.44 contour, the boundary of equal critical strain, is close or not reproduced in
  all three of its drawings (Figs. 3(a), 4(a), 5(g)). Each drawing flattens at the printed 1.65,
  above the equations' contour. This settles that the printed 1.65 is the plotted value
  (`q_fig_boundary_flat`, extending `q_boundary_165`).
- Fig. 3(b): L = 11 and 16 reproduced, 25 and 40 close (plotted a few percent above); L = 5 see above.
- Fig. 5: e_m at points A and B reproduced. At C, D, E the start of the green wrinkle branch lies
  about 1% of the strain below the equations' e_m (not reproduced); F is close
  (`q_fig5_branch_start`). This settles the reading asked for in `q_points_AF_diamonds`.
- The von Karman circles of Fig. 7 are now data for a relation with huang2005 (`q_fig7_vk_circles`).

## Left out

- Fig. 1 (p. 2): drawings of the bilayer, no values.
- Fig. 4(b), 4(c) (p. 4): schematic bifurcation diagrams; the axes carry symbols (e_B, e_F, d_B, d_F)
  but no numbers.
- Fig. 4(d), 4(e) (p. 4): crease depth against strain from the finite element simulations. The
  curves are all the same blue, labelled only by numbers, fold back on themselves (subcritical) and
  cross each other, especially in (e). The simulations cannot be rerun (`q_crease_fe`), and the one
  shared value, the snapping forward strain near 0.36, is printed (`eF_compliant_layer`).
- Fig. 4(f), 4(g) (p. 4): colour maps of the log strain in deformed meshes, no curve values.
- Fig. 5(b)-(e) (p. 5): the other marked strains (e_B, e_F, e^fc_Maxwell, e^wc_Maxwell) are
  finite element results at curve crossings and tips, marked only by arrows. They are not read here.
  They could be read in a later pass if a crease model enters the corpus. The e_F diamond at 0.36 in
  5(c) and 5(f) is the printed crease strain.
- Fig. 6 (p. 7): micrographs of the experiments, no values (the onset strains are printed and recorded).
