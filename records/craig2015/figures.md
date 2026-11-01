# Figures of craig2015

Every reading is by the record's own code: one stub per reading in `figures/`, each naming the printed
tick labels it matches and calling shared code (`_kit.py`, and in the second pass `_pastel.py`,
`_blackbars.py`, `_s3b.py`, `_fig3dots.py`; method and intervals in each docstring). Crops are at
1200 dpi. Each reading was run on the rendered crop as the build runs it, and its overlay (magenta
crosses, green bar ends) was inspected: the marks sit on the intended dots, exes, bars and curves.
Where several curves share a panel, the overlays of all its readings were also merged into one image
and checked together.

## First pass

| Panel | Readings | What | Notes |
|---|---|---|---|
| Fig. 4(c) (p. 10) | `fig4c_peak`, `fig4c_peak_F0`, `fig4c_vpeak` | traction-peak location (dots, grey error bars) and flow at the peak / v* (blue exes) against F | raster MATLAB panel (6 px blocks), grey frame; ticks paired top/bottom and left/right |
| Fig. 4(f) (p. 10) | `fig4f_peak`, `fig4f_peak_F0`, `fig4f_vpeak` | the same with b = 0 | as Fig. 4(c) |
| Supp. fig. 2(a) (p. 21) | `figS2a_peak`, `figS2a_vpeak` | peak location and flow at the peak against lambda | vector panel, black frame and black error bars; the y = 6 tick merges with the frame, so 0, 2, 4 are used |
| Supp. fig. 2(b) (p. 21) | `figS2b_lam1`-`_lam4` | flow speed profiles, lambda = 1-4 (blue, green, red, cyan) | inner ticks only (2, 4, 6 and 0.2-0.8); the legend's sample lines are dropped |
| Supp. fig. 2(c) (p. 21) | `figS2c_lam1`-`_lam4` | traction profiles, lambda = 1-4 | inner ticks only (0.04, 0.08) |
| Supp. fig. 4(a) (p. 23) | `figS4a_peak`, `figS4a_vpeak` | peak location and flow at the peak against b | blue exes near 0 overlap the frame: their intervals are wide |
| Supp. fig. 1(a) (p. 20) | `figS1a_flow` | measured lamellar flow, four bars (WT, 2, 5, 10 uM Y-27632) with error bars | categorical x axis, positions 1-4 |
| Supp. fig. 1(b) (p. 20) | `figS1b_force` | measured total force, four bars with error bars | as (a) |
| Supp. fig. 1(c) (p. 20) | `figS1c_points`, `figS1c_fit` | the four measured points (x read from the image) and the drawn Eq. 11 fit curve | the curve crosses the dots; small gaps are closed before finding dot cores |

The blue exes in Figs. 4(c), 4(f), S2(a), S4(a) are drawn as a light 'x' with a darker mark and dash
beside or below it; what the second mark is is not said, so the value is the centre of all blue marks at
that x and the interval spans them all (about +/- 0.1 to 0.14 in units of v*).

The error bars on the model's traction-peak locations (about +/- 0.2 um) and on the measured data of
supplemental figure 1 are not explained in any caption (`error_bars: unstated`).

## Second pass (this pass)

Every model curve below is run with the record's model at the panel's printed parameters (sweep over
the read x positions) and compared (`reproduction`), except where noted. The myosin density, its
gradient, adhesion density, myosin force and viscous force come from the new model `clutch_fields`
(built from `clutch_profile`'s solver: same equations, grid and settings; viscous force = lambda V'' =
T - Fmyo by Eq. 5).

Curves are read at x = 0.5, 1, ..., 7.5 um. A position is left out of a reading's `at` where the curve is
hidden under curves drawn after it (no pixel of its colour in that column; typically where several
curves lie on top of each other near 0, or near x = 0 where all curves start together). Black curves are
read away from x = 2, 4, 6, whose tick marks are black too.

- **Fig. 2(d), left (p. 4)**, `fig2d_paxillin`: measured paxillin intensity / maximum, 16 black bars
  (0.5 um bins centred at 0.25 ... 7.75). Raster; grey frame; x from the top ticks 2, 4, 6 (the bars hide
  the bottom ones), y from the left ticks 0.2-0.8 (the tall bars hide the right ones). The top edge is
  found at half-way between paper and bar on the blurred profile; interval = blur width + misfit + 4 px
  (the two full-height bars, which must be 1, read 0.995). No error bars are drawn. No model in this
  record predicts an intensity (the model's adhesion density at the Fig. 3 control-cell fit would, but
  those parameters are not printed: q_fig3_parameters).
- **Fig. 2(d), right (p. 4)**, `fig2d_myosin`: measured myosin intensity / maximum, 16 bars centred on
  0, 0.5, ..., 7.5 um (the first is half cut by the axis; note the two panels bin differently). The x = 6
  top tick is hidden, so x uses the ticks 2 and 4 (x only picks the bar); the first bar hides the left
  0.2 tick, so y uses the right ticks. The maximum bar reads 1.000.
- **Fig. 2(b) (p. 4)**: left out. Clouds of several hundred single measurements (flow and traction at
  points of one cell), overlapping into blotches where dense; there is no summary (mean, bin, error bar)
  to read, and single points cannot be told apart. They come from [14].
- **Fig. 3, left and middle (p. 9)**: left out. The model-fit lines are drawn in the same black as the
  dense measured dots and are about as thick as a cluster of them; where the cloud is dense (x > 5 in
  (b), most of (a)) line and dots cannot be told apart. The dots are single measurements as in Fig. 2(b).
  The fit parameters are not printed either (q_fig3_parameters).
- **Fig. 3, right (p. 9)**, `fig3a_adh`, `fig3b_adh`, `fig3c_adh`: the filled black markers (adhesion
  density / maximum, 'squares' in the caption), every marker with x read from the image. Raster, grey
  frame, inner ticks only ((c): the right 0.6 tick is hidden by markers, so 0.8, 0.4, 0.2). Elongated dark
  blobs (merged dashes of the whisker series) are rejected by shape. Markers merged with each other or
  with the frame are not read (about 0.15 um near x = 5.5-5.9 in (a); the last marker at x = 8 in (c)).
  The maxima read 1.00 (b), 1.000 (c), 0.998 (a). No run: fit parameters not printed. The whisker
  series (myosin density) is left out: light grey 'x' glyphs on a grey line with an unexplained dark
  dash beside each (the same style as the Fig. 4(c) exes), which cannot be read without guessing which
  mark is the value.
- **Fig. 4(a), (b), (d), (e), (g), (h) (p. 10)**, `fig4{a,b,d,e,g,h}_F*`: flow and traction profiles,
  six pale curves each (F from the legends of (a), (d), (g); blue, green, red, cyan, magenta, yellow).
  The first pass left these out as indistinguishable; at 1200 dpi the six hue clusters are well apart
  (hue histogram of (b): red 350, yellow 65, green 90, cyan 175, blue 245, magenta 290 deg), so they are
  read by hue window and saturation floor (`_pastel.py`). Raster, grey frame, inner ticks. Where the
  curves bundle (near x = 0, and where two curves run together), a light fringe of one curve can fall
  into another's hue window (a yellow fringe first read as the green curve in (a) at x = 0.5), so a
  position is read only where no other curve's pixels lie within one raster block (6 px) of the curve:
  many positions below x ~ 1.5 and some where two curves touch are therefore left out, and the green
  F = 2 curves of (a), (b) are read only over part of their length. Runs:
  `clutch_profile` at lambda = 3, gamma = 1000 with (a), (b) b = 15, v* = 0.3; (d), (e) b = 0; (g), (h)
  b = 15 and v* >> 1, entered as the added `vstar_large_added` = 1000 (alternatives 10, 100, 1e6).
  (d), (e) are also run at the added lambda = 1 (`lam_fig4def_alt`, runs `run_fig4{d,e}_F*_lam1`), see
  below. In (g) the top corner tick sits 12 px inside the frame and, the ticks being evenly spaced, was
  taken for the 0.8 tick at first (values down to -0.18); the (g) stubs drop ticks within 20 px of the
  frame (`inner_margin=20`). Check used for every Fig. 4 panel: the calibrated frame top and bottom fall
  on the axis limits (1 and 0; 0.12 and 0 in (e); 1.5 in (h); 0.4 in (i)) within 0.004.
- **Fig. 4(i) (p. 10)**, `fig4i_T` (the 'black' curve, which this raster draws in light grey, about as
  grey as the frame: read as neutral pixels away from the frame and the tick columns), `fig4i_Fmyo`
  (blue), `fig4i_Fvisc` (red), all by `_pastel.py`: force balance at F = 10, b = 15, v* = 0.3 (caption).
- **Supp. fig. 1(d), (e) (p. 20)**, `figS1d_fit`, `figS1e_fit`: the thick black model-fit curves (flow,
  nm/s; traction, Pa), read over the blue clouds with a dark-colour mask (x of (d) from the top ticks
  only: the bottom ones sit among the dots and do not pair). No run: dimensional, and V0, T0 are not
  printed (q_S1de_scales). The blue clouds of single measurements are left out as Fig. 2(b).
- **Supp. fig. 2(d), (e) (p. 21)**, `figS2d_lam1`-`4`, `figS2e_lam1`-`4`: myosin and adhesion density,
  lambda = 1-4 (F = b = 0, v* = 0.3, gamma = 1000). In (d) the lambda = 1 curve leaves the top of the axes
  at x ~ 5.6 and is read only below it.
- **Supp. fig. 3(a)-(c) (p. 22)**, `figS3a_V`, `figS3a_T`, `figS3b_g*`, `figS3c_g*`: flow and traction
  (black, red) and myosin density and gradient for gamma = 0.1-2000, F = b = 0, v* = 3. The caption does
  not give lambda: runs use the added `lam_S3_added` = 3 (alternatives 1, 2, 4). Panel (b) has no top
  frame line (the legend box replaces it), so it has its own calibration (`_s3b.py`: bottom ticks for x,
  right ticks 1, 2 for y).
- **Supp. fig. 4(b)-(i) (p. 23)**, `figS4b_b*` ... `figS4f_b*` (b = 0-100, legend of (b)) and
  `figS4{g,h,i}_{T,Fmyo,Fvisc}` (b = 10, 40, 100, caption): flow, traction, myosin density, myosin force,
  adhesion density and the force balance at lambda = 3, F = 1, v* = 0.3, gamma = 1000.

The kit's legend filter used to drop every short flat piece of a curve's colour, which also removed flat
stretches of real curves cut short by crossings (e.g. the gamma = 0.1 line at M = 1); second-pass
readings use `legend_text=True`, which drops a flat piece only when dark legend text lies just to its
right. First-pass readings are unchanged (the default is the old rule).

## What the readings settle (second pass)

- Fig. 4(a), (b), (g) and the force balance of (i) (myosin and viscous force) are reproduced or close at
  the captioned parameters; supplemental figure 4(b), (g) likewise.
- Fig. 4(d), (e) are not reproduced at any position with the captioned lambda = 3 and are reproduced or
  close with lambda = 1 for most curves: new question `q_fig4de_profiles_lambda`, which largely settles
  `q_fig4def_lambda`.
- Supplemental figure 3(a): its traction peak (0.11 at x ~ 2 um) is the height v*/e for v* = 0.3, not 3;
  it is not reproduced at the captioned v* = 3 (lambda added as 3) but is close at v* = 0.3, lambda = 1,
  and its flow equals the lambda = 1 flow of supplemental figure 2(b) (`cmp_figS3a_V_vs_figS2b_lam1`
  reproduced). This bears on `q_S3_vstar`: new question `q_S3_figure_vstar`. Panels (b), (c) are run at
  the printed v* = 3 only and are not reproduced.
- Supplemental figure 2(d), (e): the myosin density lies just above the model everywhere, the adhesion
  density just outside the reading intervals (`q_S2d_myosin_offset`, a discretisation question).
- Supplemental figure 4(c)-(f), (h), (i) at large b: the sharp peaks are not reproduced in height and
  place (`q_S4_profiles_large_b`, as `q_S4a_numerics` for panel (a)). Panels (c) and (i) draw the same
  b = 100 traction curve; read independently, they agree.
- Fig. 4(h) (v* >> 1): reproduced or close for F = 0, 5, partly for larger F (the dip and bump near
  x = 1-2 um). Fig. 4(i) traction: close except near its peak.
- Fig. 2(d) (measured paxillin and myosin profiles), Fig. 3 right (adhesion density of three fits) and
  supplemental figure 1(d), (e) (fit curves) are recorded with no run (parameters not printed).

## Left out

- Fig. 1 (schematic) and Fig. 2(a), (c) (micrographs): no values.
- Fig. 2(b), the dots of Fig. 3 (left, middle) and of supplemental figure 1(d), (e): clouds of single
  measurements with no summary, not separable where dense (see above).
- Fig. 3 left and middle fit lines: same colour as, and not separable from, the dense dots (see above).
- Fig. 3 right, the whisker series: ambiguous marks (see above).
- Supplemental figures 5-7: the model variants (uniform, step-function and density-proportional myosin
  force) are not modelled in this record; their curves are not read in this pass.
