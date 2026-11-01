# Figures of chan2008

Calibrated readings are in `figures.yaml`; check images are in `figwork/<reading id>.png`
(magenta: value and interval). Misfit is the largest distance, in pixels, of an axis mark from
the fitted scale (x, y). There were two passes.

- **First pass** (declarative `curve`/`markers` readings at 300 dpi): Fig. 1D, the Fig. 3D
  simulation and markers, and Fig. S1. None of these figures' axis lines are dark enough for
  `figure axes`. Fig. 1 and 3 are faint grey scans, and Fig. S1 has light grey vector axes. So
  the marks are the plot-box edges (which carry the end labels), gridlines and ticks, found as
  minima of the median grey profile across the plot. The eye-read data (`v_fig1d`,
  `v_figS1A_*`, `v_figS1B_nc45`, `v_figS1C_nc145`) are kept beside these readings.
- **Second pass** (2026-10-31, readings by the record's own code in `figures/*.py`, at
  900–1200 dpi): every measurement plotted as bars, histograms or points with error bars that the
  first pass left out. Each code file calibrates its axes from the image (box edges, gridlines
  and tick strokes matched in order to the printed labels named in the file) and reports its
  misfit in each reading's note. Files that serve several readings share code. `_matlab_bars.py`
  serves the MATLAB bar charts of Fig. S4, S5 and S11D. `fig3c_260.py`, `fig4d_strain.py`,
  `figS8C_control.py` and `figS12E_points.py` are each used by a second reading of the other
  colour or curve. Every file that uses shared code pins it by its SHA-256, so the build cache,
  which is keyed on the reading's own file, cannot serve a stale reading.

## Main text

- **Fig. 1A, 1B** (p. 3): left out. A schematic and cartoon snapshots, with no values.
- **Fig. 1C** (p. 3): left out. One stochastic trace of xsub against time (and an inset). It is a
  single realisation, so a seeded run cannot reproduce it point by point, and the record has no
  trace output to compare with.
- **Fig. 1D, flow** (p. 3): read (first pass). `fig1d_flow` (0.5–70 pN/nm) and `fig1d_flow_soft`
  (0.12–0.3 pN/nm) both read the solid line. The purple marker at the minimum and the orange
  marker at 100 pN/nm break the trace, so the line is read in two parts. x: box edges 0.1 and 100
  plus the gridline at 10 (log10). y: box edges 120 and 60 plus gridlines 110–70. Misfit 0.00 px x,
  0.47 px y. Data `v_fig1d_read`, `v_fig1d_soft_read`, compared with runs at 5 ms and 0.625 ms.
- **Fig. 1D, traction** (p. 3): read (first pass). The faint dashed line is read in four boxes
  that hold only the dashed line (`fig1d_traction_soft`, `_band`, `_band2`, `_stiff`). The right
  axis is calibrated by its faint inner ticks at 30, 20 and 10 pN. Misfit 0.00 px x, 0.50 px y.
  Nothing is read near 1.2–2 pN/nm, where the dashed and solid lines cross.
- **Fig. 2A–D** (p. 4): left out. Micrographs, a time projection and kymographs (2C, 2D): images
  of single beads, with no axis values to read.
- **Fig. 3A, 3B** (p. 4): left out. Image and kymograph. The in-panel 123 ± 6 and 152 ± 8 nm/s
  are single-filopodium examples that no model run targets.
- **Fig. 3C** (p. 4): read (second pass), bar by bar. `fig3c_hist_260` (blue, 260 Pa, n = 95) and
  `fig3c_hist_57k` (red, 57 kPa, n = 258) cover the 10 nm/s categories 0–230. The 'More' category
  is not read because its label is not a number. x: the box edges and the tick strokes below the
  axis give the category width. The label blobs "0", "40" … "200" fall on categories 0, 4 … 20
  (misfit 0.03 category), which gives 10 nm/s per category. x is Excel's category label, the
  bin's upper edge. y: the axis line (0.00) and the dashed gridlines every 0.02, found as minima
  of the bar-masked grey profile (9 marks, misfit 1.83 px). Each bar's top is where its colour
  ends. The interval is the edge blur plus the misfit, about ±0.001. A category with no bar
  reads 0. Data `hist_fig3c_260`, `hist_fig3c_57k` (measured). No model in the record predicts a
  distribution. The printed in-panel means (`v_fig3c_260`, `v_fig3c_57k`) stay as recorded.
  Checks: the blue bars are whole multiples of 1/95, each colour sums to 1, and the bin-centre
  means agree with the printed means (q_fig3c_counts).
- **Fig. 3D, simulation** (p. 4): read (first pass). `fig3d_sim_rise`, `fig3d_sim_upper`,
  `fig3d_sim_stiff`. Misfit 0.90 px x, 0.30 px y. Not read: the simulation below 1 kPa, where it
  runs on the experiment line, and inside the grey "Cell Death" band.
- **Fig. 3D, experiment** (p. 4): read twice. First pass: means only, one `markers` reading per
  colour (`fig3d_exp_*`, kept). Second pass: `fig3d_exp_sem` reads all six squares with their
  error bars at 1000 dpi. The error bars are SEMs: the SOM's statistical analysis counts "the
  number of SEMs a given experimental point deviated from simulation". Markers are the strongly
  coloured blobs; the legend's marker is dropped because it lies below 70 nm/s. Error-bar ends
  are the caps: the strongest stroke darkening both sides of the bar near the end of its dark
  run, measured against the brighter flank. This keeps the connecting and dashed lines that cross
  the bars from passing for caps. x: box edges 0.1 and 100 and the label blobs "1" and "10"
  (4 marks, misfit 1.98 px). The read x values land on the gel moduli named in the paper (260,
  730 Pa; 1.1, 1.3, 24, 57 kPa). y: box top and bottom and 3 gridlines (5 marks, misfit 1.45 px).
  The bars come out symmetric about each mean, within a few tenths of nm/s. Datum
  `v_fig3d_exp_sem` → run `run_fig3d_exp_sem` → validation `val_fig3d_exp_sem`, which now carries
  the measured SEM.
- **Fig. 4A–C** (p. 5): left out. Phase and fluorescence images and a 3-D intensity rendering, with
  no axis values.
- **Fig. 4D** (p. 5): read (second pass) at 1200 dpi. `fig4d_hist_strain` (blue, Bead Strains) and
  `fig4d_hist_ref` (red, REF Bead RMS) cover the 5 nm bins from 0 to 100 nm. The blue "100+"
  overflow bar is not read: it has no bin centre. x: box left edge (label "0") and the inner tick
  strokes at 25, 50, 75 and 100 along the top edge (5 marks, misfit 3.40 px). y: axis and box top
  plus the right-edge ticks at 0.1–0.4 (6 marks, misfit 2.55 px). Bin centres are midway between
  the blue and red bars of a group, on an even grid fitted to the groups found. The blue bars from
  72.5 nm up are too short to keep their colour in the scan. They are read as the top of the dark
  stub on the axis, with a wider interval, and the reading says so. Each colour sums to 1 within
  the reading (blue with the unread 100+ bar). No model in the record predicts these.
- **Fig. 4E** (p. 5): read (second pass). `fig4e_tension` reads the two bars (730 Pa, 1300 Pa)
  with their SEM error bars ("mean ± SEM", caption). y: box top 10, axis 0 and gridlines 2–8
  (6 marks, misfit 0.91 px). Values are multiplied by the axis factor 1e-5. Caps are found as rows
  where the dark stroke through the error-bar column is at least twice the line's own width, with
  rows on gridlines skipped. On the red bar the contrast is lower, so the threshold is lowered
  there. The code would mirror a cap it cannot find about the bar top, and say so, but none was
  needed. Datum `tension_fig4e` (measured). The stored-energy model (Eq. 9) is not in the record.

## Supporting Online Material

- **Fig. S1A–C** (p. 33): read (first pass). `figS1A_koff01`, `figS1A_koff03`, `figS1A_koff003`
  (with `_stiff`), `figS1B_nc45` (with `_soft`), `figS1C_nc145`. Misfit ≤ 0.5 px. Left out: the
  red line of A between 1 and 7 kPa (a single stochastic jump), and the repeats of panel A's
  curves in B and C.
- **Fig. S2** (p. 34): left out. Each scatter is one bead's positions over a recording: a single
  random trajectory with no summary values.
- **Fig. S3** (p. 35): left out. Image sequences.
- **Fig. S4** (pp. 36–47): third column read (second pass). There are 67 per-bead step-size
  histograms: `figS4a_bead01`–`29` (260 Pa, pp. 36–40), `figS4b_bead01`–`17` (730 Pa, pp. 41–43)
  and `figS4c_bead01`–`21` (1300 Pa, pp. 44–47). All use `figS4_hist.py`, with x edges ±1, ticks
  −0.5, 0, 0.5 and y edges 0 and 120, ticks 20–100. The code stops on any panel whose tick strokes
  do not fit these labels, and none did (misfit ≤ 0.3 px x, ≤ 3.11 px y). Crops come from the
  histogram box tops found on 150 dpi renders. Bar tops are taken at the centre of the bars'
  black outline, as the axis line is. A one-count bar reads about 1.2, inside its interval. Every
  histogram's counts sum to about 180, the number of steps in a ~181-frame recording (Fig. S11A).
  Left out: the first two columns (each bead's positions and its normalized trajectory: single
  random trajectories). The printed "Max = … nm" values are not recorded.
- **Fig. S5A–C** (p. 48): read (second pass). Each panel's main axes (`figS5A_main`,
  `figS5B_main`, `figS5C_main`; x edges ±1, y edges 0 and 0.6, misfit ≤ 2.4 px) and both insets
  (`figS5*_inset_neg`, `figS5*_inset_pos`; x ticks ±0.3, ±0.6, ±0.9 read along the top edge
  because the bars' outlines pass for ticks at the bottom; y 0 to 0.01, misfit ≤ 0.33 px). In the
  insets the bin spacing comes from neighbouring bars, or from the bar width (MATLAB's 0.8 of a
  bin) when no two bars are adjacent. The insets read the small bins (> 0.3, < −0.3) far more
  precisely than the main axes, which give 0 where a bar is no taller than the axis line. The
  printed in-panel Max/Mean/Stdev Fail values are not recorded.
- **Fig. S5D** (p. 48): read (second pass). `figS5D_failures` reads the three diamonds with their
  error bars. x (log): the tick strokes under 100, 1000 and 10000 (misfit 0.03 px). The read x
  values land on 260, 730 and 1300 Pa. y: box and gridlines (6 marks, misfit 0.46 px). The error
  bars are not described anywhere (`error_bars: unstated`). The fitted line and its printed slope
  are not read. No model output gives failure rates (q_failure_frequency_model).
- **Fig. S6, S7** (pp. 49–50): left out. Kymographs and micrographs.
- **Fig. S8A, S8B** (p. 51): left out. Micrograph and kymograph (the 143 nm/s is a single example).
- **Fig. S8C** (p. 51): read (second pass). `figS8C_control` (lavender) and `figS8C_gfp`
  (magenta) read the bars on 260 Pa and 24 kPa with their error bars (kind not stated). y: box
  top 180, axis 0 and gridlines every 20, from the gap between the bar groups (10 marks, misfit
  2.01 px). x is the group label in Pa. Caps are found as in Fig. 4E. Runs `run_figS8C_control`
  and `run_figS8C_gfp` sweep the model over the two moduli, with validations `val_figS8C_control`
  and `val_figS8C_gfp`. See q_figS8C_vs_fig3 for how the transfected bars sit beside Fig. 3C/3D.
- **Fig. S9** (p. 52): left out. Micrographs.
- **Fig. S10A–C** (p. 53): left out. Drawings and an image. **S10D**: left out. Two single bead
  traces; its printed <T> and <δ> are already recorded.
- **Fig. S11A–C** (p. 54): left out. A: images. B: one drift track (a single trajectory). C: a
  cloud of several hundred overlapping crosses that cannot be told apart; its printed RMS
  (5.2 nm) is a single value, not a reading.
- **Fig. S11D** (p. 54): read (second pass). `figS11D_hist`, 1 nm bins from 0 to 16 (x 9 marks,
  misfit 3.33 px; y 4 marks, misfit 0.20 px). The axis says only "Frequency", and the bars sum to
  neither 1 nor 100, so the datum is the height as plotted.
- **Fig. S12A–D** (p. 55): left out. Synthetic images and a kymograph. **S12F**: already recorded
  from its printed table.
- **Fig. S12E** (p. 55): read (second pass). `figS12E_points` reads the eleven open squares, found
  as hollow outlines; a horizontal closing bridges the square that the red line at shift 0 cuts.
  `figS12E_curve` reads the red fitted Gaussian at the integer shifts, except at 0, where the red
  vertical line covers it. x: the tick strokes under −5 … 5 (10 marks, misfit 2.94 px). y: the
  tick strokes left of the box (8 marks, misfit 2.21 px). The two are not compared, because the
  build pairs table values by position and the curve has one value fewer. The printed s = 1.20
  is not read.

## What the figures say about open questions

- **q_eq13_delta / q_fig3d_not_compared.** The Fig. 1D flow (κsub in pN/nm), the Fig. S1A black
  line (E in kPa) and the Fig. 3D simulation (E in kPa) give the same values at the same numbers
  on x. They plot one simulated curve with κsub [pN/nm] equal to E [kPa] in number
  (q_fig_same_curve), which bears on how Δ enters Eq. 13.
- **q_fig3c_labels.** The Fig. 3C bars confirm that n = 95 goes with the 260 Pa gel. Only the
  caption's "stiff"/"soft" words are swapped (q_fig3c_counts).
- **Validations with measured errors.** `val_fig3d_exp_sem` replaces the first-pass validations'
  reading-only intervals with the measured SEMs. `val_figS8C_*` add the untransfected flow.
- **q_figure_readings.** The calibrated readings supersede the decade-tick eye readings for
  verdicts. The eye-read data are kept, unchanged.
