# Figures of trujillo2008

Figure pass (2026-11-18). Every reading is `mode: code`; all share one reading code (`figures/*.py`, the
same body with a different CONFIG block). Axes are calibrated from the image: the plot box is the
longest dark lines, the inward tick marks on the bottom and left spines are matched in order to the
printed tick labels (corner labels on the perpendicular spine where the label sits there), and the
mirror ticks on the top and right spines (or, on a log axis, the minor ticks at 2..9 per decade) are used
as a check. Markers are found by template matching of each marker shape (sizes as drawn in the figure or
its legend) on the dark-ink mask; error bars by their caps along the marker's column. Misfits below are
the largest residual of the tick fit, then of the check ticks, in pixels at the reading's dpi.

- **Fig. 2(a)** (p. 3), stability diagram, 1200 dpi: read as `fig2a_flat` (8 open circles) and
  `fig2a_creased` (12 filled triangles). x misfit 1.0 px, y 1.3 px (mirror ticks agree to the same). The
  triangles are centred on their centroid; in rows shared with circles they sit within 3 px of the circles'
  centres, which shows the figure places triangles that way. The dashed boundary is drawn by hand and is
  not read. Data: `fig2a_flat_points`, `fig2a_creased_points` (inputs of `ec_from_swelling`).
- **Fig. 2(b)** (p. 3), l/l0 of unconstrained gels, 1200 dpi: read as `fig2b_bis02` (open circles, 5),
  `fig2b_bis04` (filled triangles, 5), `fig2b_bis07` (open squares, 7: two overlapping squares at 24 mol%
  and two at 28 mol%) and `fig2b_bis10` (filled diamonds, 5), each with both ends of its error bar (kind
  not stated). x misfit 1.6 px, y 0.8 px (mirror 1.3 px). Caps merged with a fit line on one side are
  still found from their clean end; caps inside a filled marker are not visible, and a bar end hidden in
  its marker is reported as at most the marker edge. Where several markers share a column, caps are
  paired with markers so that bars are as nearly symmetric as possible, and the outer interval spans every
  cap of the column (24 mol% squares, 28 mol% squares). The best-fit lines are not read: the record
  refits them (`ec_from_swelling`). Data: `fig2b_l_bis02` ... `fig2b_l_bis10`, with the legend values
  `legend_bis02` ... `legend_bis10`. Compared through `rep_ec_interpolation`: the paper's interpolation
  re-run on these points reproduces every Fig. 3(a) value at the same composition
  (question q_ec_interpolation_rerun, which answers q_ec_interpolation).
- **Fig. 3(a)** (p. 4), e_c against bis(acrylamide) content, 900 dpi: read as `fig3a_ec` (9 open triangles,
  including three nearly coincident at 0.4 mol%, separated by their own base lines) and `fig3a_ec_fig2_series`
  (the same code, `at` the four Fig. 2 compositions). Log x axis on the 10^-1 and 10^0 ticks (misfit 0.5 px;
  minor/mirror ticks 3.6 px), y misfit 1.0 px. No error bars are drawn; the caption says the uncertainties
  are about the size of the markers, so each point's interval is the marker height. The dashed line
  (Biot's 0.334) is not read: it is the model. Compared with `biot_vs_crosslinker` point by point
  (`val_biot_fig3a_points`: close; 6 of 9 within, the 0.05, 0.1 and 2.0 mol% points outside), with the
  printed mean 0.33 +/- 0.02 (`con_mean_fig3a`: reproduced, mean 0.327) and with the re-run interpolation
  (`rep_ec_interpolation`). This settles the audit's request in q_ec_trend_vs_mean and q_figures_not_read;
  see q_fig3_trend_point_by_point.
- **Fig. 3(b)** (p. 4), e_c against film thickness, 900 dpi: read as `fig3b_ec` (10 open circles: 1 at 3 um,
  2 at about 60 um, 3 at 200 um, 4 at 1 mm; overlapping circles are separated by pairing their own top and
  bottom crossings of the column). Log x axis on 10^1, 10^2, 10^3 (misfit 0.7 px; check 2.8 px), y misfit
  1.0 px; the 1 mm points are drawn at about 1060 um. Uncertainty = marker height, as for Fig. 3(a).
  Compared with `biot_vs_thickness` (`val_biot_fig3b_points`: close; 9 of 10 within, one 1 mm point at about
  0.365 outside) and with the printed mean 0.33 +/- 0.01 (`con_mean_fig3b`: reproduced, mean 0.332).
- **Fig. 3(c-e)** (p. 4): left out: optical micrographs of creases, no values to read (the crease spacing
  is described, not measured).
- **Fig. 4** (p. 5), h/h0 of 1 mm attached gels, 1200 dpi: read as `fig4_flat` (4 open circles) and
  `fig4_creased` (3 filled triangles), with error bars (kind not stated). The top y label is misprinted
  "1.5" (q_fig4_axis_label): the axis is calibrated on 1.6-2.2 and the bottom corner 1.5 only (misfit
  1.1 px; x misfit 2.0 px), which puts the top spine at 2.30 (q_fig4_top_label_settled). At 16 mol% a flat
  circle and a creased triangle overlap (each centre's interval tripled; caps shared); at 19 mol% two
  triangles share four caps; at 10 mol% the column carries two pairs of caps for one visible circle (a
  hidden second sample cannot be read; the outer interval spans all caps). Compared through the
  reconstructed mid-point rule `onset_thickness_ratio` with the printed 2.0 +/- 0.1 (`con_onset_fig4`:
  reproduced, about 1.98); see q_fig4_same_composition.
- **Fig. 1** (p. 1): left out: a schematic and a micrograph, no values.
- **Fig. 5** (p. 5): left out: micrographs of creases before and after de-swelling, no values.
