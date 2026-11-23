# Figures of panzetta2023

All readings are made by the record's own code: `figures/_p23.py` (the method, described in its
docstring), `figures/_specs.py` (what each reading reads: printed axis labels, grey band, where to start)
and one stub per reading in `figures/`. The figures are raster images in the PDF, of two kinds:

- **MATLAB plots** (Figs. 4, 5, 7A, S2, S3): a full frame with inward ticks. The ticks along the left
  and bottom frame lines are found in the image and matched to the printed labels (on log axes, the
  1-9 x 10^k ticks of each decade): the map that puts the most labelled values on ticks, fitted by least
  squares. Misfits are 0.7-1.4 px on x and 0.7-1.3 px on y at 800 dpi (S3 x 1.4 px, S2 x 1.2-1.9 px).
- **Excel charts** (Figs. 3, 6, 7B, 8, 9): a frame without ticks; each label is a block of text beside
  the frame, centred on its value, so label centres matched in order give the calibration.
  Category axes (bar charts) are taken in order.

Intervals (95%) add half the line or run height, half a pixel, the y misfit, the slope times the x misfit,
and half the jump where a gap (dashes, a marker of another curve) is interpolated across.

## Read

- **Fig. 3A-D** (p. 5, bars, nc = 50 and 400, ks = 1 pN/nm): `fig3a_canonical`, `fig3a_modified`,
  `fig3b_*`, `fig3c_*`, `fig3d_*`. Each bar's end from its grey band (light grey canonical, dark grey
  modified, black in C), with its error bar: the caps are short runs of the error-bar grey (lighter than
  the dark bars, darker than the light ones) centred on the bar; where a cap lies inside a bar of the same
  grey it is taken as the mirror of the other (the note says so). The caption does not say what the error
  bars are (`error_bars: unstated`). A and C are compared with `flow_nc_axial` (canonical: ks^eps0 = 0,
  added). B is labelled [nN] though it is a position; it is recorded in nm, D in nN as printed, and
  neither is compared: the model's position and forces are positive in the retrograde direction while
  the figure plots them negative, and the force unit looks wrong (`q_fig_force_units`).
- **Fig. 4A, 4B** (p. 6): `fig4a_canonical`, `fig4a_modified` (l = 100 nm), `fig4b_canonical`,
  `fig4b_modified` (l = 1000 nm), 14 nc from 11 to 900. The grey curve is followed in its grey band
  after the dilated black dashes are removed; the dashed curve in the black band, across its gaps. In
  4B the two curves overlap: the grey one is read where it shows beside the dashes, and the two
  canonical readings (4A, 4B) are compared with each other as a check of the reading
  (`cmp_f4_canonical_ab`). Fig. 4A is the only evidence for the claim that a short orthogonal spring
  shifts the optimum up (p. 5): the l = 100 nm curve's minimum lies near nc = 800 against about 400.
- **Fig. 5A** (p. 6, ks = 0.1 pN/nm): the seven strains, `fig5a_e0` ... `fig5a_e3`. The grey levels of
  the five grey curves overlap in the image, so all ink is one mask (open markers filled by a closing),
  and on the left (nc 11-25) the seven curves, apart there, are read by their order from the top
  (strain 3 on top). Strain 0 is also followed through to nc 120-180 on the right; there the other
  curves merge into thick bands and are not read. nc 12 and 14 are left out: a gap of the dashed
  strain-0.1 line leaves six runs in every column near them.
- **Fig. 5B** (p. 6, ks = 1 pN/nm): `fig5b_e0` ... `fig5b_e3`, by order where the seven curves lie
  apart (nc 48-264). The positions lie halfway (in log nc) between the 20 simulated nc that carry the
  markers, where no open marker splits a line; there the figure draws straight segments between points.
  Strain 0 at nc = 100 reads 94.0, as Fig. 4B's dashed curve (94.0), the same simulation.
- **Fig. 6** (p. 7): `fig6_soft` (grey markers, left axis, strains 0.1-3) and `fig6_stiff` (black, right
  axis, 0-3): markers are what is left of the series' grey band after an opening wider than the line.
  The grey marker at strain 0 is hidden behind the black one. The black marker at 0 reads 443.9 (printed
  445), at 3 about 750 (+69 % printed: 752); the grey at 3 about 80.9 (+103 % of 40: 81.2). At 0.1 the
  grey reads about 40.8, +2 % where the text prints +3 % and +1 clutch (`q_fig6_soft_01`). Both are
  compared with the optimum search run at each strain (`optimal_nc_axial`).
- **Fig. 7A** (p. 7, transverse strain, ks = 1 pN/nm): `fig7a_e0` ... `fig7a_e1`, by order (strain 1 on
  top) at nc 100-200. Beyond, the dashed and dotted lines' gaps let a column hold four runs that are not
  the four curves (seen on the overlay at nc 350 and 400), so those positions were dropped.
- **Fig. 7B** (p. 7): `fig7b`, the four markers (an Excel chart with a light frame). They read 444.7,
  728.6, 758.5, 780.4: increases of 64 %, 70 % and 75 % over the marker at 0, against the printed 64,
  71 and 76 %: the figure agrees with the text.
- **Fig. 8A, 8B** (p. 8): `fig8a_soft`, `fig8a_stiff`, `fig8b_soft`, `fig8b_stiff` (ids follow the
  caption's colours: grey = 0.1, black = 1 pN/nm). Markers as Fig. 6. In 8A the black markers at 0 and
  0.1 are behind the grey ones and are not read. These are checked against Fig. 6 (`normalise_optimum`,
  with the printed 40 and 445) under the caption's assignment and swapped, and 8B against the secant
  slopes of 8A (`secant_slope`). **This settles a question the figure raises**: the black curve of Fig. 8
  is the soft substrate's (ending near 2.02 = 81/40) and the grey the stiff one's (1.69 = 750/445), the
  reverse of the caption; the text's saturation on the stiff substrate is the grey curve of 8B
  (`q_fig8_colours`).
- **Fig. 9A-D** (p. 8, bars at the Fig. 6 optima): `fig9a_soft`, `fig9a_stiff`, `fig9b_soft`,
  `fig9b_stiff`, `fig9c_soft`, `fig9c_stiff`, `fig9d_soft`, with error bars (unstated). The dark grey
  bars (ks = 0.1, left axis) stand in front of the light grey ones (ks = 1, right axis); a light bar is
  read where it shows beyond the dark one (all of A and B; C at strains 0-1). Its run continues the dark
  bar, bridging the translucent caps drawn across the bars. Each series' error bar is the pair of caps
  whose midpoint is its bar end; a pair not found is left unread (no mirroring, which could take the
  other series' caps). In C at strain 3 the bar tops show a darker overlap whose series cannot be told,
  so the dark bar there may read the overlap's lower edge; D's light bars are hidden behind the dark
  ones. Not compared: the averages are at the paper's optima, which the record's model does not
  reproduce (`q_soft_optimum`, `q_stiff_optimum`); a later reading can run `flow_nc_axial` at the Fig. 6
  optima.
- **Fig. S2** (p. 12, supplement): `figS2l_all` (flow against ks) and `figS2r_all` (flow against nc).
  The three strains' marker series lie on one curve within a marker, which is the figure's point (the
  original model is insensitive to residual strain); they are read together, where each column holds
  that one curve (left of the legends). The figure does not say nc (left) or ks (right): added as 40
  and 0.1 pN/nm (`added.yaml`), from where the minima lie. Run with 1000 k events as the caption says,
  one seed. **This bears on `q_soft_optimum`**: Fig. S2 (right) is the canonical model on (by its
  minimum) the soft substrate, falling to a minimum of about 73.5 nm/s near nc = 40, as Fig. 5A; the
  comparison `cmp_fS2r` shows whether the record's canonical model does the same.
- **Fig. S3** (p. 13): `figS3_solid`, the solid curve (deformed length 1000 nm, undeformed 500 nm at
  strain 1, from the text p. 7). The dashed curve (l = 2000 nm) lies on it within a line width except near
  nc 300-700, where it is up to about 0.3 nm/s higher; it cannot be read apart and is left out.

## Left out

- **Fig. 1** (p. 2) and **Fig. S1** (p. 12): drawings of the model.
- **Fig. 2** (p. 4): single stochastic trajectories against time (substrate position, engaged clutches,
  flow), one random run each; their averages are Fig. 3.
- **Fig. S3, dashed curve**: indistinguishable from the solid one (above).
- **Fig. 5A right of nc ~ 30 (except strain 0) and Fig. 5 between the crossing points**: the curves
  cross and merge; positions there cannot be assigned to a strain.

## Questions the figures bear on

- `q_figures` (figures not read): now read as above.
- `q_soft_optimum`, `q_stiff_optimum`: Figs. 5A/5B, 6 and S2 are compared point by point with the record's
  model; see the comparisons `cmp_f5*`, `cmp_f6_*`, `cmp_fS2*`.
- `q_s3_caption`: Fig. S3's curves overlap, so the figure cannot tell which length was held at 1000 nm;
  `cmp_fS3_solid` runs the text's reading (undeformed 500 nm).
- New: `q_fig8_colours`, `q_fig_force_units`, `q_fig6_soft_01`.
