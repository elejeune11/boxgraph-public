# Figures: cao2012

Every plot is read by calibrated code (`figures/<reading id>.py`, all built on the shared
`figures/_cao.py`; its docstring gives the method). The plots are embedded bitmaps of about
150 dpi, rendered at 1200 dpi, so one source pixel is an 8 x 8 block: line positions are
quantized in 8-px steps and the intervals include half a step. Axes are calibrated from the frame
lines (blue in Figs. 2-7, dark grey in Figs. 8, 11, 13) and the tick marks found in the image,
matched to the printed labels; the misfit quoted is the largest residual of that fit, added to
every interval. Each reading was checked with `boxgraph figure check` and its overlay.

The paper has no measurements: every plotted value is a prediction, of the exact bifurcation
analysis (curves) or of the finite element model (markers). The curves are compared with runs of
the record's models swept over the read x positions; the markers have no runnable model
(`fe_postbifurcation`) and are recorded as predicted data for later papers.

## What the readings show

- The plotted exact-analysis curves reproduce: Figs. 2, 3 (mu_f/mu_s >= 10), 5, 6 (left), 7, 8 and
  13 all reproduce, and Fig. 11 is close (the model sits 0.003 below the green line at
  mu_f/mu_s = 5-10). Fig. 2's e0 line reproduces Eq. 5.
- `q_eW_ratio30_ratio5` is settled by Figs. 2 and 8. Their eW at mu_f/mu_s = 5 and 30 agrees with
  the record's analysis (0.165, 0.052), and Fig. 8 excludes the caption values ≈ 0.175 and
  ≈ 0.055 (new question `q_fig_eW_ratio30_ratio5_settled`).
- Fig. 4: for 1.5 <= mu_f/mu_s <= 2.25 the analysis puts lambda0_1s = 1.5 on the line labelled 2,
  and 2 on the line labelled 1.5 (new question `q_fig4_pre1p5_pre2_swapped`).
- Fig. 6 (right): the analysis's kh is 0.02-0.045 above the plotted lines, about the size of the
  zigzag of the paper's own lines (new question `q_fig6b_kh_offset`).
- Fig. 13 bears on `q_audit_ridge_twice_eW`: eMR/eW rises from about 1.5 at mu_f/mu_s = 100 to about
  3.8 near 1000, so "roughly twice" holds only near 150-300 (new question `q_fig13_ridge_ratio`).
- The marker readings agree with the strains printed elsewhere: Fig. 8 ePD = 0.198 at
  mu_f/mu_s = 30 (text: e_PD ≈ 0.2); Fig. 11 ePD = 0.320 at 186 (Fig. 12: onset evident at 0.314,
  a snapshot); Fig. 13 eMR = 0.0359 [0.0353, 0.0365] at 837 (Fig. 14: a ridge has formed at the
  snapshot 0.0367, so the onset is at most that). These markers have no runnable model, so the
  build compares none of them.

## Panel by panel

- **Fig. 1 (p. 2)**: left out; a drawing of the geometry and the modes, no values.
- **Fig. 2 (p. 2)**: read. `fig2_eW` (lower line, eW) and `fig2_e0` (upper line, Eq. 5) at
  mu_f/mu_s = 1.5-500; seeds are the lower and upper line at mu_f/mu_s = 1.2. Calibration x: frame
  (1, 1000) and ticks 10, 100 (log); y: frame (0, 0.6) and ticks 0.1-0.5; misfit 5.8 px (the y
  ticks are unevenly spaced by up to 8 px in the bitmap). Beyond mu_f/mu_s of about 20 the two
  lines lie in one 8-px line, so both readings give the same value there, with an interval that
  covers either. Runs: `bilayer_plane_strain` and `simple_formula_plane`.
- **Fig. 3 (p. 3)**: read, the four solid eW lines (`fig3_eW_pre1`, `_pre1p5`, `_pre2`, `_pre3`)
  at mu_f/mu_s = 10-500 (lambda0_1s = 1.5 only to 200: at 500 the trace cannot tell its line from
  the dashed lines crowding it), seeded at mu_f/mu_s = 7 (before the dashed lines start) as the 1st-4th
  solid line from the bottom; legend and the label box blanked. The order (bottom to top
  lambda0_1s = 1, 1.5, 2, 3) follows the label's leaders, and the lowest line agrees with Fig. 2's
  eW within the intervals. Below mu_f/mu_s = 10 the lines cross (magnified in Fig. 4), so they are
  not read there. Calibration x as Fig. 2; y log: ticks 0.01, 0.1 and frame 1; misfit 2.3 px.
  The dashed e0 lines (Eq. 5) are left out: over most of the range each lies within a line width
  of a solid line and its dashes cannot be traced apart from it; Eq. 5 is read in Fig. 2.
- **Fig. 4 (p. 3)**: read, four eW lines over 1 <= mu_f/mu_s <= 5, seeded at mu_f/mu_s = 2 where
  all four are apart (from the bottom: lambda0_1s = 2, 1.5, 1, 3, by the label's leaders; the
  lambda0_1s = 1 line is the one that starts at 0.456). Calibration x: frame 1, 5 and ticks 2-4;
  y: frame 0, 0.5 and ticks 0.1-0.4; misfit 4.3 px. The lines for lambda0_1s = 1 and 1.5 touch
  near mu_f/mu_s = 2.6-3 and the trace cannot tell which leaves the tangency where; the lines for
  1 and 2 then merge towards mu_f/mu_s = 5. Only the unambiguous ranges are read:
  `fig4_eW_pre1` 1.25-2.25, `fig4_eW_pre1p5` 1.5-2.25, `fig4_eW_pre2` 1.5-3.5, `fig4_eW_pre3`
  1.25-4.5.
- **Fig. 5 (p. 3)**: read, `fig5_eW`, the single line at lambda0_1s = 1.1-5.5, mu_f/mu_s = 1.
  Calibration x: frame 1, 6 and ticks 2-5; y: frame 0.3, 0.5 and ticks 0.35, 0.4, 0.45; misfit
  3.9 px. Run: `bilayer_plane_strain` swept over lambda0_1s.
- **Fig. 6 (p. 4), left**: read, the four solid kh lines (`fig6a_kh_pre*`) at mu_f/mu_s = 15-500,
  seeded at mu_f/mu_s = 11 as the solid line nearest kh = 0.53, 0.60, 0.66, 0.74 (bottom to top,
  lambda0_1s = 1, 1.5, 2, 3); label and legend blanked. Calibration x: frame 10, 1000 and tick 100
  (log); y: frame 0, 1.2 and ticks 0.2-1.0; misfit 4.3 px. The dashed k0h lines are left out for
  the same reason as in Fig. 3. Compared with the `kh` output of `bilayer_plane_strain`.
- **Fig. 6 (p. 4), right**: read, the four kh lines (`fig6b_kh_pre*`) at mu_f/mu_s = 1.5-4.5,
  seeded at mu_f/mu_s = 4.7 (bottom to top lambda0_1s = 1, 1.5, 2, 3, by the leaders). The lines
  are polygons through values computed at about 0.05 decade steps; their jags show that the
  paper's kh at the flat minimum of eW is itself scattered by about +-0.02, beyond the reading's
  interval. Calibration x: frame 1, 5, ticks 2-4; y: frame 0.5, 1, ticks 0.6-0.9; misfit 4.5 px.
- **Fig. 7 (p. 4)**: read, the four solid eW lines for uniaxial stressing (`fig7_eW_pre*`) at
  mu_f/mu_s = 5-500 (lambda0_1s = 1 only to 200: beyond, it is hidden in its dashed e0 line),
  seeded at mu_f/mu_s = 7. Below mu_f/mu_s of about 3 the lines converge on 0.556 and are not
  read. Calibration x as Fig. 2; y log: frame 0.001, 1 and ticks 0.01, 0.1; misfit 5.9 px. Run:
  `bilayer_uniaxial`. Dashed e0 lines (Eq. 6) left out as in Fig. 3.
- **Fig. 8 (p. 5)**: read. `fig8_eW`, the navy theory line (colour mask), mu_f/mu_s = 3.2-70;
  `fig8_eF` (blue triangles, 5 points) and `fig8_ePD` (dark red hexagons, 6 points), marker
  centroids; legend symbols blanked. Calibration x: frame 1, 100 and the major tick 10 (minor
  ticks dropped by length); y: frame 0, 0.30 and major ticks 0.05-0.25; misfit 2.1 px.
- **Figs. 9, 10, 12, 14 (pp. 5-7)**: left out; deformed-mesh snapshots, no axes. Their strains
  are in the captions and are in `data.yaml`.
- **Fig. 11 (p. 6)**: read. `fig11_eW`, the green theory line (lambda0_1s = 1.3), mu_f/mu_s =
  3.2-500; `fig11_eF` (dark red hexagons, 3 points) and `fig11_ePD` (blue spheres, 5 points).
  Calibration x: frame 1 and major ticks 10, 100; y: frame 0, 0.35 and major ticks 0.05-0.30;
  misfit 1.8 px.
- **Fig. 13 (p. 6)**: read. `fig13_eW`, the black theory line (lambda0_1s = 2), mu_f/mu_s =
  4.3-1000; `fig13_eMR` (red spheres, 11 points). Calibration x: frame 1 and major ticks 10, 100,
  1000; y: frame 0.25 and major ticks 0.00-0.20; misfit 2.4 px.
