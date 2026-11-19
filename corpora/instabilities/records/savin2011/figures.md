# Figures of savin2011

Read on 2026-11-19 by the record's own code (`mode: code`). Every reading runs `figures/<id>.py`, a stub that
calls the shared code in `figures/_common.py` with the panel's entry in `figures/_specs.py`. The vector panels
are rendered at 1200 dpi, so each plot box is 1500–4000 px on its shorter side.

**How the axes are calibrated.** The frame is the lowest long black row and the leftmost long black column.
Tick candidates are short black runs standing on the frame lines. The printed labels are matched to them by
`match_ticks`: the straight line, in log10 for log axes, that puts the most labels within 6 px of a candidate.
It needs at least three labels (two where stated), distinct candidates and at least 15 px per label. On stage
axes the frame's left edge, at E7, anchors the first label. This makes the calibration ignore stray marks, such
as a black line or a symbol standing on the axis, and survive ticks hidden under points. The largest misfit of
the matched ticks is added to every interval; it is under 0.5 px for every vector panel.

**How points are read.** Points are pixels of the series' colour, with thin lines (fit curves, bars) stripped by
an opening with a disk. Each marker is read at the centre of its box: ±(misfit + 2 px). A marker partly hidden
by another symbol or a line is located by fitting a template of its own shape and size (disk, square, diamond,
triangle or ring) to the visible part: ±4 px. Markers that run together are not read. Error bars are followed
along the marker's column, through other symbols drawn over them. An end inside the marker is reported as "at
most the marker". An end that stops against other ink gets an outer interval reaching the far side of that
ink. Bars are s.d. in every figure (captions of Figs. 1, 3, 4, 5, S1, S3, S6, S8, S9; Figs. S10 and S11 are
"the same as in Figure S9").

**Bars.** Bar charts are read at the median top edge of each bar, with the black s.d. bar along its centre.
Raster panels without tick marks (Fig. 1b) are calibrated on the centre rows of their printed label text,
with a quarter of the text height added to every interval.

## Read

- **Fig. S8b, c (p. 17)**: λ and R of the chick at E8, E12, E16. Readings `figS8b_obs`/`figS8c_obs` (black
  squares, measured), `figS8b_sim`/`figS8c_sim` (filled light-purple circles: the lattice simulation, the only
  per-stage output of the non-runnable `lattice_simulation`), and `figS8b_eq3`/`figS8c_eq4` (open purple
  circles: Eqs. 3 and 4). y ticks 0, 4, 8 mm (b) and 0, 1, 2 mm (c); misfit 0.3 px. Several symbols overlap:
  the E16 open circle in c is fitted as a ring, and bars hidden behind other symbols are followed through them.
  Compared with Table 1 by stage (`lam_obs_t1`, `lam_cm_t1`, `R_obs_t1`, `R_cm_t1`; consistency), the
  simulation with the measurements (validation), and Eqs. 3/4 with the simulation (approximation).
- **Fig. 3b (p. 3)**: ro and ri of the chick, E8–E16. Readings `fig3b_ro`, `fig3b_ri` (all stages), and
  `fig3b_ro_t1`, `fig3b_ri_t1` (E8, E12, E16, compared with the Table 1 footnotes). Misfit 0.4 px.
- **Fig. 3c (p. 3)**: Lt (`fig3c_Lt`, `fig3c_Lt_t1`) and Lm (`fig3c_Lm`), E8–E16. The inset photograph is
  excluded. The Lm point at E8 lies under the Lt point and is not read; the E8 Lt point is fitted as a partly
  hidden disk.
- **Fig. 3d, e (p. 3)**: stress–strain points of the chick mesentery (`fig3d_E8/E12/E16`) and tube
  (`fig3e_E8/E12/E16`), each with its y s.d. bar. In d the 0 and 50 % ticks lie under the points on the axis,
  so x is matched on 100, 150, 200. Points near zero stress that run together are not read (about 5 per stage
  in d).
- **Fig. 3f, g (p. 3)**: Em, Et (log axis, 10³–10⁶ Pa) and ε₀ at E8, E12, E16 (`fig3f_Em`, `fig3f_Et`,
  `fig3g_e0`), compared with the Table 1 footnotes.
- **Fig. 4b, c (p. 4)**: log-log, minor ticks matched (10…90 in b; 1…10 and 20 in c); misfit under 1 px.
  - `fig4b_chick`, `fig4c_chick`: the three chick squares. Run through Eqs. 3 and 4 divided by ro, the
    diagonal lines (models `eq3_scaled_line`, `eq4_scaled_line`), as validations.
  - `fig4b_rubber`, `fig4c_rubber`: the green rubber-model triangles that do not overlap a neighbour (8 of about
    14 in b, 10 of about 16 in c), as fit quality, since Eqs. 3/4 were fitted to them. No bars are read for
    the triangles: they stand in shared columns, and their bars cannot be told apart. Their intervals add 9 px
    for where the plotted point lies within a triangle.
  - The chick E8 bar of Fig. 4b reaches λ/ro ≈ 40, above Table 1's 4.6 ± 1.0 mm over ro = 155 µm (≈ 36). The
    plotted bars presumably include the spread of ro; Table 1 does not say.
- **Fig. S3 (p. 10)**: force against distance for the three beads (`figS3_rb0398`, `figS3_rb0253`,
  `figS3_rb0122`). Log-log; x ticks 2–9 with 1 on the axis line; y decades 10⁻⁶–10⁻³; misfit under 1 px.
  Points touching their neighbours at large d are not read (14, 16 and 22 points are). Each is swept through
  `magnet_force_law` with Table S1's F0 and α, as fit quality.
- **Fig. S6c (p. 14)**: the six bimaterial-strip simulations (`figS6c_pts`, origin run). Log-log, every minor
  tick matched. Swept through the new model `strip_fit_line` (y = 0.36 k1/k2), as fit quality. The SI says the
  line fails near k1/k2 = 10.
- **Fig. S1 (p. 8)**: cells per mm² in the eight slices a–h of the E12 tube (`figS1_bars`, x = 1…8 for a…h),
  each with its s.d. bar.
- **Fig. 1b (p. 2)**: proliferation bar charts, which are raster panels without ticks, calibrated from the
  label text: E5 tube (3 bars), E12 tube (20 bars), E5 mesentery (3), E12 mesentery (14). Readings
  `fig1b_E5_tube`, `fig1b_E12_tube`, `fig1b_E5_mes`, `fig1b_E12_mes`; x is the region's order, from anterior.
  A few E12 bars show no s.d. bar above the bar and are read without one. No model predicts these values;
  they are recorded as measurements.
- **Figs. S9 (quail), S10 (finch), S11 (mouse) (pp. 19–20)**: panels a, b, c, f and g against stage, and d, e
  stress–strain, for each species (the coloured series; the grey chick series repeat Fig. 3 and are not read
  again). Readings `fig<S9|S10|S11>{a_h, b_ro, b_ri, c_Lt, c_Lm, f_Em, f_Et, g_e0}` cover every plotted stage.
  The `…_t2` readings hold only the stage of Table 2 (quail E12, finch E13, mouse E16.5), compared with its
  footnotes. The stress–strain readings are `…d_<stage>` and `…e_<stage>`. The mouse stages fall on half days
  (E12.5–E16.5). The species plot more stages than the captions name (e.g. quail h at E12, E14, E15 and E16,
  and quail Lt from E8). In S11d only the 150 and 200 % ticks are visible, so it is calibrated on those two.
  The volume insets of S9c–S11c are excluded (see below).

## Left out

- **Fig. 5b, c (p. 5)**: the species points are open black squares, diamonds and triangles and black crosses.
  They overlap in a cluster near λ/ro ≈ 16 and share crossing bars of the same colour. The caption does not
  say which symbol is which stage (two per species), so a value could not be attached to its stage. The
  stages Table 2 gives are recorded there. The rubber and simulation points repeat Fig. 4.
- **Fig. 4b, c and Fig. 5b, c, simulation (blue rings)**: stacked open rings at the same abscissa in b, and
  overlapping rings crossed by their own bars in c. A ring could not be told from its neighbours, and a trial
  reading put its marks between rings.
- **Fig. S3 inset (p. 10)**: F0 and α against rb. These are the Table S1 fit parameters, already entered as
  printed values (the inset adds nothing that is not printed).
- **Figs. S9c–S11c insets**: tube and mesentery volumes against day (log axis, about 1.2 × 0.9 cm on the
  page). Their exponential fits are the printed growth rates (`rate_tube_measured`, `rate_mesentery_measured`).
  The points sit on the fit lines in the same colours and cannot be told from them. Not read.
- **Figs. S4c, S5b (pp. 11, 12)**: several sample stress–strain curves (red/blue) crossing one another, and
  their black average. The average is the curve that Fig. 3d, e plots as points (E16), which is read there.
  The individual samples cannot be told apart.
- **Fig. S4b, S5a**: tracked lengths drawn over a sequence of movie frames (a single trajectory per sample).
- Drawings, photographs, micrographs and renderings with no values: Fig. 1a, c, d; Fig. 2; Fig. 3a and the
  insets of Fig. 3b–e; Fig. 4a; Fig. 5a; Figs. S1 (micrograph half), S2, S4a, S6a, b, S7, S8a.

## What the figures settle

- **q_table_s1_vs_fig_s3**: Fig. S3, read, agrees with Table S1 (comparisons `cmp_figS3_*`). The question's
  comparison assumed points at d ≈ 1.6 mm. In fact the plotted points begin at d ≈ 1.8 (smallest bead), 2.2
  (middle) and 2.6 mm (largest). There, e.g., 0.105 N × (1/2.575)^4.08 ≈ 2.2 × 10⁻³ N, which is what is
  plotted. See the new question q_fig_s3_consistent.
- **q_table_model_rows**: Fig. S8's open circles reproduce Table 1's "Computational model" rows at every stage,
  for λ and R. The filled circles (the simulation) are a separate series: e.g. λ at E8 is about 5.4 mm against
  6.1 mm for Eq. 3. This supports reading the rows as Eqs. 3 and 4, not as the simulation.
- **New finding (q_sim_lambda_E16)**: the simulation's λ at E16 (about 7.9 mm) misses the measured 9.5 ± 0.5 mm.
  Their bars do not overlap.
- **Rubber models (q_rubber_scatter)**: the rubber points scatter about Eqs. 3/4 beyond the precision of the
  reading. Their bars could not be read, so these verdicts do not weigh the experimental spread.

## Verdicts at the time of this pass

- **Reproduced:**
  - every Fig. 3 point against the Table 1 footnotes (ro, ri, Lt, Em, Et, ε₀ at E8, E12, E16);
  - every Fig. S9–S11 point against the Table 2 footnotes at the tabulated stage (21 comparisons);
  - Fig. S8 squares and open circles against Table 1;
  - all 52 Fig. S3 points against Table S1's power laws;
  - the Fig. 4c chick points against Eq. 4.
- **Close:**
  - the Fig. 4b chick points against Eq. 3 (E8 and E12 close);
  - Fig. S6c against the 0.36 line (close only at k1/k2 = 10, as the SI says);
  - Eqs. 3/4 against the simulation in Fig. S8.
- **Not reproduced:**
  - the simulation against the measurements for λ at E16;
  - the rubber points against Eqs. 3/4, by reading precision only.
- **q_force_range**: the plotted calibration forces span about 10⁻⁶ to 2.2 × 10⁻³ N over the plotted d. The
  1 mN upper end of Methods is the order of the largest plotted force; the larger forces that Table S1 gives at
  d = 2 mm for the two larger beads lie outside the plotted range of d for the largest bead.
