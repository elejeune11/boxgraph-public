# Figures of mekhdjian2017: what was read and what was left out

Two passes. The first read the model curves (Figs. 5c-d, S4c-e) and the Fig. 5e measurements; the second
(2026-11-22) read every other plot of data, measurements included, whether or not a model predicts them.
Every reading is the record's own code in `figures/`, run by each build on the page region at its `dpi`.

How the second-pass code works. Each file is written from shared templates (one y-axis and bar reader, plus a
box-plot or an x-y reader where needed); the settings at the top of each file say which panel and which
bars, boxes, points or line. The y axis is calibrated on its tick marks (outside or inside the axis line, found row
by row so a slightly tilted scan is followed), matched to the printed labels; ticks hidden behind a label or a
data line are filled in only where the visible ones are evenly spaced, and an axis without ticks (Fig. 7b inset,
Fig. S6) is calibrated on the vertical centres of its labels. The x axis of point and line plots is calibrated the
same way (Fig. S2b on a log10 axis). Each value's note gives the calibration and its misfit; the interval adds
the line thickness and the spread of the edge across the bar. Bars: the value is the centre of the top edge, the
upper error-bar end the centre of its cap; the lower end is hidden in the bar and taken as the mirror of the upper.
Categorical bars and boxes are indexed by `condition_index` (1, 2, 3 ... from the left, listed in each reading's
`what`). All overlays were checked: the marks sit on the bar tops, medians, markers and lines meant.

## Read

- **Fig. 1d** (p. 3), PyMT spheroid invasion in 3D collagen, soft / stiffened / soft + TGFβ, mean ± SEM:
  `fig1d_area`, `fig1d_protrusions`, `fig1d_single` (7, 7 and 9 tick marks; misfit ≤ 0.02 units). The soft
  bar of the area panel has a very short error bar that was read from its cap.
- **Fig. 2b, 2d** (p. 4), transit time through constrictions and percentage passing, PyMT Ctrl / + TGFβ / Met1:
  `fig2b_transit` (mean ± SEM), `fig2d_passing` (SE of the binomial distribution, recorded as `sem`).
- **Fig. 3e** (p. 5), AFM indentation stiffness on 2.7-kPa gels: `fig3e_stiffness` (misfit 5.7 Pa).
- **Fig. 3g** (p. 5), nuclear protrusion ΔL against time, 24 points each (5-120 s): `fig3g_tgf` (light
  grey-blue), `fig3g_ctrl` (dark blue); error bars (SEM) read at both ends where they leave the marker. The legend
  marker of the upper series lies on the path at 70 s; the reader follows the series from point to point so it is
  not taken. One TGFβ error bar (95 s) is hidden by neighbouring markers and has no interval.
- **Fig. 4b, 4d** (p. 6), average traction stress and total traction force on 2.7-kPa gels: PyMT Ctrl / + TGFβ /
  Met1 (`fig4b_stress`, `fig4b_force`) and MCF10AT Ctrl / + TGFβ (`fig4d_stress`, `fig4d_force`), mean ± SEM.
- **Fig. 5c-d, S4c-e, 5e**: first pass, unchanged (see below).
- **Fig. 6d, 6f** (p. 8), molecular tension sensor force per sensor and total force per cell, box plots
  (median in red; the legend defines the box as 25th-75th percentiles and the whiskers): `fig6d_sensor`,
  `fig6d_total`, `fig6f_sensor`, `fig6f_total`. The value is the median; quartiles and whisker ends are in each
  note. Single points beside the boxes are not read.
- **Fig. 7b** (p. 9): the inset bars (mean adhesion lifetime ± SEM, `fig7b_lifetime`, calibrated on label centres:
  the inset axis has no ticks) and the two cumulative distributions, solid Ctrl and dashed + TGFβ, at 5-50 min
  (`fig7b_ctrl` as the lower green line, `fig7b_tgf` as the upper; read in a window wide enough to span the
  dashes). Beyond 50 min both lines lie on the x axis and are not read.
- **Fig. 7d, 7i** (p. 9), adhesion length (mean ± SEM) and paxillin axial position: `fig7d_length`, `fig7i_axial`
  (its y axis starts at 20 nm; error bars not defined in the legend).
- **Fig. 7f, 7h** (p. 9), box plots with black medians: `fig7f_corr` (paxillin-tensin correlation; the Ctrl median
  lies at the lower quartile and is read as that line), `fig7h_ctrl`, `fig7h_tgf` (axial position of six adhesion
  proteins, MCF10A and MCF10A + TGFβ).
- **Fig. 9e, 9f** (p. 12), Met1 spheroid invasion with paxillin WT / Y31/118F and with dasatinib: `fig9e_area`,
  `fig9e_single`, `fig9f_area`, `fig9f_single` (minor ticks between the labelled ones skipped).
- **Fig. 9g** (p. 12), Kaplan-Meier survival, low (black) and high (red) paxillin, every 12 months to 120:
  `fig9g_low`, `fig9g_high`. The black line is taken as the highest black line up to 48 months (the legend lies
  below it there) and as the lowest beyond (the hazard-ratio text lies above it there).
- **Fig. 9h** (p. 12), RPPA SRC-pY416 score, box plots: `fig9h_rppa`; the thick median of the control box is
  partly covered by data points and is read as the row inside the box that is dark across most of its width.
- **Fig. S2b** (p. 32), relative spread area of MCF10AT against fibronectin (log axis): `figs2b_ctrl` (blue),
  `figs2b_tgf` (red) at 0.01, 0.1 and 10 µg/mL. One error bar (+TGFβ at 10 µg/mL) merges with the dashed
  significance line and has no interval.
- **Fig. S3c** (p. 33), MCF10A with control or high α5 integrin: `figs3c_area`, `figs3c_stress`, `figs3c_force`.
- **Fig. S5** (p. 35), spread area and total force on the four PA gels and on MTS coverslips: `figs5_area_ctrl`,
  `figs5_area_tgf`, `figs5_force_ctrl`, `figs5_force_tgf` (x = gel modulus) and `figs5_area_mts`,
  `figs5_force_mts` (condition 1 Ctrl, 2 + TGFβ). The PA-gel bars are the Fig. 5e bars replotted
  (`cmp_fig_*_s5_5e_*`); the untreated and TGFβ simulated areas are validated against them as well (`val_A_s5_*`).
- **Fig. S6** (p. 36), paxillin axial position in paxillin-/- MEFs, WT against Y31/118F: `figs6_axial` (label
  centres; the axis line at 0 is not labelled and is not used).
- **Fig. S7** (p. 37), PINCH fluorescence in adhesions and paxillin-PINCH correlation, box plots with red medians:
  `figs7_pinch`, `figs7_corr` (inside ticks at every half label step; minor ones skipped).
- **Fig. S8a** (p. 38), immunoblot fold changes over GAPDH (no error bars): `figs8a_ctrl` (all 1.0 by
  normalisation), `figs8a_tgf`.
- **Fig. S10** (p. 40), hazard ratios of five genes: `figs10_hazard`. The paxillin bar reads 1.46, the value the
  text prints (p. 11); the FAK bar reads about 1.36 against the text's 1.34. These are not set as comparisons
  because the figure datum is indexed by condition and the text values are scalars.

First pass (unchanged):

- Fig. 5c-d (p. 7): the two simulated cells (solid nm = 250/nc = 150, dashed nm = nc = 500), traction stress
  and spread area at nine moduli (0.1-50 kPa).
- Fig. S4c-d (p. 34): the four reinforcement rates (kadd = 0, 0.01, 0.1, 1.0 /s). The dashed (0.1 /s) line
  merges with the others below ≈ 0.15 kPa, so its 0.1 kPa point is not read.
- Fig. S4e (p. 34, both panels): the black (no reinforcement) and orange (12 pN) lines.
- Fig. 5e (p. 7): MCF10A spread area, average traction stress and total traction force, Ctrl and +TGFβ, on the
  four PA gels, with the upper ends of the error bars (lower ends hidden in the bars, taken as mirrors; the
  legend does not say what the bars are).

## What the new readings settle or bear on

- q_total_force_product: Fig. S5 shows the same total forces as Fig. 5e, so the 2-3x excess over stress times area
  is in the data as plotted twice; Fig. S3c, from the same laboratory, does follow stress times area
  (new question q_s3c_product).
- q_mts_stiffness: the MTS bars are now data (new question q_mts_readings), still without a modulus to run a model at.
- No new reading is an output of the record's clutch models except the S5 spread areas; the 3D invasion data
  (Figs. 1d, 9e-f) and the constriction data (Fig. 2) are recorded for later models.

## Left out, with the reason

- Fig. S4e blue lines (Fthresh = 5 pN): the parameters that go with them are not given (q_fthresh5_inputs);
  nothing in the record could be compared with them. (First pass.)
- Fig. 6b (p. 8): the FRET-efficiency and force histograms have no values on their count axes ("Pixel Count"
  without tick labels), so no count can be read; they are the calibration of the sensor, not a result.
- Fig. 3d (p. 5): one representative force-indentation curve (a single trace).
- Fig. 3c (p. 5): 3D surface plots of elasticity over single cells (perspective drawings, no readable axes).
- Fig. 8b (p. 11): a colour-coded heat map of spectral counts for about 60 proteins; colours on a five-step scale
  and row labels too small to attribute, so no value can be assigned to a protein.
- Fig. S3a (p. 33): FACS scatter plots with gates; the printed gate percentages are numbers, not plotted data.
- Micrographs, TFM displacement and stress maps, SAIM and FRET images, immunoblots, schematics: Figs. 1a-c, 1e-g,
  2a, 2c, 3a-b, 3f, 4a, 4c, 5a, 6a, 6c, 6e, 7a, 7c, 7e, 7g, 7j, 8a, 8c-f, 9a-d, 9f (images), 10; S1, S2a, S3b,
  S6 (images), S7 (images), S8a (blots), S8b-c, S9.
- Fig. 5b and Fig. S4a-b: the model schematic and parameter tables (their values are in data.yaml as printed).
