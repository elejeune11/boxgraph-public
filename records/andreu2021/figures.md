# Figures of andreu2021

Every plotted value in the record is read by code (`mode: code`) from the page rendered at 1200 dpi. The
first pass read the four model lines of Fig. 2e (`figures/_fig2e.py`). The second pass (2026-11-01) read
all plotted measurements with one shared module, `figures/_kit.py`, and a thin file per reading,
`figures/<reading id>.py`. That file holds only the printed tick labels, the series colour and which
labels are read, and it pins the kit's SHA-256. Reading ids are the datum id plus `_fig`. Each reading's
overlay was checked: every mark sits on the intended point, mean line, bar end or bin top.

How the kit reads (details in its docstring):
- **Calibration** comes from the tick marks found in the image. They are matched in order to the
  printed labels and fitted linearly, or in log10 for log axes. Broken y axes (Fig. 3d, e, h, i) are
  calibrated per segment. Break marks (//) and segment-end marks are told apart from ticks because they
  cross the axis line. Misfits are 0–1.8 px, and 2.6 px on the x axis of Supplementary Fig. 2a.
- **Markers**: a disk of the marker's radius is matched to the series colour. Other ink may cover it and
  paper may not. A fully visible marker is located to ±1–2 px. For a marker partly behind another
  series, the interval spans every position it could have. Error-bar ends are the centres of the caps.
  When an end is hidden behind another series it is taken as the mirror of the visible end, and the
  outer interval covers the hidden span. A bar that does not leave its marker is reported as "at most
  the marker".
- **Scatter plots with mean ± s.e.m.**: the mean is the longest, thickest dark run in the group's band.
  Dots drawn over the line are bridged. The s.e.m. bar is the dark stem with its caps. Dots crossing
  the stem are treated as hiding it, which widens the outer interval rather than guessing.
- **Histograms**: the top of each bar at its labelled bin centre. An empty bin reads 0 ± 1.3 counts, so
  bins with 1–3 cells are at the limit of the reading.
- **Categorical x**: Ns (non-stretched) and Sq (square 1 Hz) points, and treatment groups, are separate
  readings whose x is a `condition_index`. The meaning of each index is in the datum's note. Triangular
  signals are read against frequency (Hz), time series against time (s).

## Read

- **Fig. 1b** (p. 3): `fig1b_flow_fig`, the mean actin flow on 0.6 kPa gel and on glass (2 groups). The
  s.e.m. bar does not leave the mean line. Misfit 0.9 px.
- **Fig. 1e–h** (p. 3): for each panel (2.5, 5, 10, 20% stretch), YAP on the left axis and paxillin
  adhesion length on the right, each read twice: the triangular points at 0.125–2 Hz (`fig1{e,f,g,h}_{yap,pax}_tri_fig`)
  and Ns/Sq (`..._ns_sq_fig`), all with s.e.m. bars. Misfit ≤ 1.1 px. Red points partly behind blue ones
  get wide intervals, e.g. 1e at 0.25 and 2 Hz, 1g at 1 Hz. These are the measurements Fig. 2e overlays
  on the model; they are compared in `val_fig1*_pax_*` and `val_fig2e_line_vs_fig1*`.
- **Fig. 2b, 2c** (p. 4): `fig2b_anisotropy_fig` (6 groups) and `fig2c_adhesion_fig` (4 groups), mean ±
  s.e.m. Misfit 0.4–0.5 px.
- **Fig. 2e** (p. 4), first pass: `fig2e_line_{2p5,5,10,20}`, the black model lines at 0.125–2 Hz.
  Overlays checked in this pass: the marks sit on the lines. The measured points in Fig. 2e are those of
  Fig. 1e–h (caption: "from Fig. 1"), so they are read from Fig. 1, where nothing is drawn over them.
- **Fig. 3d–g** (p. 6): bead speed, force loading rate, stiffness and paxillin recruitment vs time, the
  4 Hz (red) and 0.25 Hz (blue) series (`fig3{d,e,f,g}_{4hz,0p25hz}_fig`). 3d and 3e have broken y axes,
  calibrated per segment. In 3f the 0.25 Hz point at 0 s is entirely behind the red one and is not read.
- **Fig. 3h–k** (p. 6): the black points at 160 s, triangular 0.125–4 Hz (`fig3{h,i,j,k}_tri_fig`) and
  Sq (and Ns in 3k) (`fig3{h,i,j}_sq_fig`, `fig3k_ns_sq_fig`). In 3h and 3i the Sq point lies on the
  upper segment of the broken axis (40–80 µm/s, 5000–10000 pN/s), which is calibrated on its own two ticks.
- **Fig. 4d, 4h** (p. 7): apparent Young's modulus vs retraction speed, 8 red points each with s.e.m.
  (`fig4{d,h}_modulus_fig`). The x axis is calibrated on its 2–8 ticks; each point's x is read and lies
  on the 1 µm/s grid.
- **Fig. 4k, 4l** (p. 7): `fig4k_adhesion_fig` and `fig4l_yap_fig`, 4 groups each. In 4k the s.e.m. bars
  are drawn in red over red dots, so their ends are partly hidden and the outer intervals are wide.
- **Fig. 4n, 4o** (p. 7): paxillin recruitment vs time, control (red) and blebbistatin (blue) series.
  The control series repeat Fig. 3g exactly (same beads); `cmp_fig4n_fig3g_0p25hz` and
  `cmp_fig4o_fig3g_4hz` are reproduced.
- **Fig. 5c, 5d** (p. 8): `fig5c_yap_fig` (x = ventilation frequency 0.1, 1.1, 2.1 Hz) and `fig5d_yap_fig`
  (right and left lung at 1.1 Hz), mean ± s.e.m.
- **Supplementary Fig. 1a** (p. 13): `figS1a_yap_fig`, YAP vs gel stiffness on a log axis, calibrated on
  its long ticks 1, 10 and 100. The x positions read are 0.642, 2.370, 3.394, 5.228, 10.93, 16.92 and
  29.70 kPa. Supplementary Table 2 (p. 21) gives 0.64, 2.37, 3.40, 5.26, 10.94, 16.80 and 29.92 kPa, all
  within 1%. This is an independent check of the calibration.
- **Supplementary Fig. 1b** (p. 13): cell area, triangular points and Ns/Sq (`figS1b_area_*`).
- **Supplementary Fig. 1c, 1f, 1g** (p. 13): EdU-positive percentage (4 groups), adhesion length and YAP
  for talin 2 shRNA and control cells (4 groups each), mean ± s.e.m.
- **Supplementary Fig. 1d** (p. 13): YAP and paxillin in talin 1 knockdown cells, as Fig. 1. The
  paxillin point at 0.5 Hz is almost entirely behind the blue marker and is not read.
- **Supplementary Fig. 2a** (p. 14): `figS2a_strain_fig`, the calibration of gel strain vs voltage, with
  black points every 0.1 V. The y axis has unlabelled minor ticks every 2.5%. Its lowest (0) tick is
  covered by the marker on the axis corner and is not used (y misfit 1.8 px). The 0.0 V point (on the
  corner) and the 0.2 V point (under the orange fit line) are not found, so 0.1 V and 0.3–2.0 V are read.
  At 0.4–0.5 V the overlapping markers make the bars "at most the marker".
- **Supplementary Fig. 2b** (p. 14): `figS2b_rate_tri_fig` and `figS2b_rate_sq_fig`, the applied stretch
  rate (V/s). Compared with the slopes printed inside panels 2c–g (`figS2_slopes_printed`, 0.245–3.995
  V/s, checked on the image) in `cmp_figS2b_slopes`, which is reproduced.
- **Supplementary Fig. 3a, 3c** (p. 16): YAP and paxillin in HMVEC and SAEC, as Fig. 1. Not read
  because they lie entirely behind the blue markers: paxillin Ns and 0.125 Hz in 3a, paxillin Ns in 3c.
- **Supplementary Fig. 4b–d** (p. 17): bead displacement, force and stiffness at 0 s, triangular and Sq.
- **Supplementary Fig. 4e** (p. 17): force loading rate vs time on a log axis, three of the nine series:
  Sq 1 Hz (grey), 0.125 Hz (brown) and 2 Hz (blue), at 32–160 s. The axis is calibrated on its 100, 1000
  and 10000 ticks, because the lower ticks and the 0 s tick are covered by the markers sitting on the
  axis. At 160 s these agree with Fig. 3i (2 Hz: 34 vs 35 pN/s; Sq: 6200 vs 6400 pN/s).
- **Supplementary Fig. 5a, 5b, 5d** (p. 18): peak force vs retraction speed (8 points each), and
  adhesion length in control and blebbistatin cells (2 groups).
- **Supplementary Fig. 6a–d** (p. 19): the four YAP histograms, 15 bins each (`figS6{a,b,c,d}_hist_fig`).

## What the readings settle or raise

- `q_validation_not_read`: the measured points are now read, and the validations exist (`q_fig1_points_read`).
- `q_ksub_unit`: with k_sub as printed the model stays at 0.60 µm, so every validation against Fig. 1
  fails. With the code's value the 20% panel is close (`q_printed_ksub_flat`).
- `q_scaling` and the "largely reproduced" claim: the paper's own Fig. 2e lines miss several measured
  paxillin means by more than their s.e.m., especially at 10% stretch. The lines span about 0.69–2.12 µm
  while the measurements span about 0.70–2.54 µm (`q_fig2e_line_vs_data`).

## Not read

- **Fig. 1a, c, d; 2a, d; 3a–c; 4a–c, e–g, i, j, m; 5a, b; Supplementary Fig. 1e, 3b, 3d, 5c**:
  micrographs, kymographs, drawings, and single example traces (Fig. 3c; force–height curves of Fig. 4b,
  c, f, g).
- **Supplementary Fig. 2c–h, 4a**: single example voltage and force traces. The slopes printed in 2c–g
  are recorded as `figS2_slopes_printed`; the falling slopes and those of 2h are in its note.
- **Supplementary Fig. 4e, the other six series** (0.5 Hz, 0.25 Hz, 4 Hz, 1 Hz, 0.25 Hz+B, 4 Hz+B): these
  curves cannot be told apart. The green and the pink/red pairs are close in hue at this resolution and
  overlap in position and error bars. The 4 Hz and 0.25 Hz series repeat Fig. 3e.
- **Supplementary Fig. 4f, 4g**: nine series overlapping in position and error bars across most of the
  time range, with near-identical hues. The curves cannot be told apart. The 4 Hz and 0.25 Hz series
  repeat Fig. 3f and 3g.
- **Fig. 2e measured points**: the same data as Fig. 1e–h, read there.
