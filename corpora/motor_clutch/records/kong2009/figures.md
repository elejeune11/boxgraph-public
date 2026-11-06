# Figures of kong2009: what is read and what is left out

All readings are made by this record's code (`figures/*.py`, each a few lines of settings around the
shared helper `figures/_lt.py`), on crops rendered at 1200 dpi. The panels are vector plots; the
helper

- finds the axes as the longest dark vertical and horizontal lines, and their outward ticks, and
  matches the ticks to the printed labels (bottom to top; a broken axis is two linear segments, which
  meet where the axis line is interrupted);
- finds the open markers of one series by matching their outline (a ring, a square or a triangle)
  in the series' colour, letting grey series drawn on top stand in for the covered parts of a black
  outline; the error-bar stem runs through each marker and the joining lines run into it, so the
  inside is not required to be empty;
- takes the marker's centre (a triangle's centroid, where its lines meet) as the plotted point, with
  an interval of 2 px plus the tick misfit (plus 3 px for triangles);
- follows the SEM bar's stem from the marker's outline to the first cap (a band of rows reaching out
  on both sides of the stem), and reports a bar hidden in the marker as at most the marker, or
  mirrors a bar seen on one side only;
- with `at`, reads the line joining the markers at the given forces instead, with the larger of the
  two end points' intervals plus the slope times a 2-px column uncertainty.

The settings each file gives are the printed tick labels it matched, the colour and shape of the
series, the rough marker size, and small regions where markers are not searched for (titles, legends,
and three spots where overlapping outlines mimic a marker; see `q_overlap_artefacts`).

## Read (measured, mean +- SEM)

| Panel | Series | Datum |
|---|---|---|
| 3 A | FN / a5b1-Fc / GG-7, Ca2+/Mg2+ (circles) | lt_FN_a5b1Fc_CaMg |
| 3 A | Fc / GG-7 (grey squares) | lt_Fc_GG7 |
| 3 B | FN / a5b1-Fc / GG-7, Mg2+/EGTA | lt_FN_a5b1Fc_MgEGTA |
| 3 C | FN / a5b1-Fc / GG-7, Mn2+ | lt_FN_a5b1Fc_Mn |
| 3 C | BSA / a5b1-Fc / GG-7, Mn2+ (diamonds) | lt_BSA_a5b1Fc_Mn |
| 3 D | FN / membrane a5b1, Mg2+/EGTA (triangles) | lt_FN_ma5b1_MgEGTA |
| 4 A | P1D6 / a5b1-Fc / GG-7 | lt_P1D6_a5b1Fc |
| 4 B | FN / HFN7.1 / anti-mouse Fc | lt_HFN71_FN |
| 5 A-C | FN / tra5b1-Fc / GG-7 in the three cation conditions | lt_FN_tra5b1Fc_* |
| 6 A, B | FN / a5b1-Fc, Mn2+ with TS2/16 or 12G10 | lt_FN_a5b1Fc_Mn_TS216, _12G10 |
| 6 C | FN / tra5b1-Fc, Mn2+ with TS2/16 | lt_FN_tra5b1Fc_Mn_TS216 |

## Read as lines, for the consistency of replotted data

The triangles of Figs. 5 A-C (Fig. 3 A-C circles replotted), 6 A-B (Fig. 3 C) and 6 C (Fig. 5 C) are
read as the dashed line joining them at 10-45 pN, and the originals as the solid line joining the
circles at the same forces (`comparisons.yaml`).

## Read in the audit, for the stated high-force overlap

The Fc/GG-7 squares are read again on Fig. 5 A (`fig5a_squares`). On that panel every square above
24 pN lies on the lower y segment, so the line joining them can be read at 30-50 pN. The markers
agree with the Fig. 3 A reading to within 0.15 s. The circle curves of Figs. 3 B-C (35-50 pN) and
5 A-C (30-45 pN) are read as lines at the same forces, and each is compared with the squares
(`cmp_*_vs_FcGG7_*`, `q_high_force_overlap_overstated`).

## Read in the second pass: the other measured plots

No model in the record predicts these; they are recorded as measurements (origin `measured`), with
no run. Four more helpers do the reading:

- `figures/_bars.py` (bar charts and histograms). The y axis is calibrated on its outward ticks
  (`_lt`); each bar is found by its top edge, a long horizontal run of dark pixels with light above
  (the error-bar stem's gap bridged), standing on the axis on at least one side, so bars that touch
  their neighbours keep their own tops. Its kind is judged from its inside, left of the stem: empty
  (open), filled (closed) or partly (hatched). The value is the centre line of the top edge; the SEM
  bar's ends are the centres of its caps, the lower half mirrored where it is hidden in a filled or
  hatched bar. x is the bar's position from the left among bars of its kind (quantity `bar_position`;
  the reading's `what` lists the conditions), or for Fig. S2 A the bar's centre on the calibrated x axis.
- `figures/_s4.py` (Fig. S4: filled squares): ticks as above; squares found by an opening wider than
  the joining lines.
- `figures/_s1.py` (Fig. S1: coloured lines on a log x axis), described in the table.
- `figures/_s5.py` (Fig. S5: open circles of four colours): a ring of the circles' radius matched against
  each colour's mask; a circle is kept where at least 80% of its visible outline is in the colour and
  its inside is nearly empty of it (in a cluster, neighbouring rings cross it).

| Panel | Readings (data) | Calibration | Notes |
|---|---|---|---|
| 2 A | `fig2a_open` (`af_FN_a5b1Fc_fig2a`), 5 bars | ticks 0, 0.1, 0.2; misfit 0.3 px | 0.3 tick merged with the axis end, not used |
| 2 B | `fig2b_open`, `_closed`, `_hatched` (`af_BSA_a5b1Fc_fig2b`, `af_FN_a5b1Fc_fig2b`, `af_FN_GG7_fig2b`), 3 bars each | 5 ticks, misfit 0.8 px | Mn2+ hatched bar (0.01): cap sits on the edge |
| 2 C | `fig2c_open` (`af_FN_tra5b1Fc_fig2c`), 3 bars | 6 ticks, misfit 0.5 px | |
| 2 D | `fig2d_open`, `_closed`, `_hatched` (`af_*_fig2d`), 3 bars each | 5 ticks, misfit 0.8 px | |
| S2 A | `figs2a_closed` (11 bars), `figs2a_open` (17 bars) (`rf_hist_BSA_a5b1Fc_Mn`, `rf_hist_FN_a5b1Fc_Mn`) | y 4 ticks, misfit 0.7 px; x 19 ticks (every 5 pN) | no error bars; the fractions of each series add up to 1.00 |
| S2 B-D | `figs2b_open`, `_closed`; `figs2c_*`, `figs2d_*` (one bar each) | 4 ticks each, misfit 0.4 px | |
| S3 C | `figs3c_open` (`stiffness_by_lifetime_bin`), 3 bars | 4 ticks, misfit 0.6 px | unit taken as pN/nm (`q_stiffness_unit`); the bars' x labels are recorded as printed data |
| S4 A | `figs4a_band` (`running_af_ma5b1`) at 40-290 repeats | y 4, x 7 ticks | band of overlapping squares; interval half the band less half a square |
| S4 B | `figs4b_squares` (`af_ma5b1_vs_time`), 4 squares | y 4, x 7 ticks | first square cut by the y axis |
| S5 A-D | `figs5{a,b,c,d}_{k,r,g,b}<force>` (`lnN_s5*`), 16 series | y 6-7, x 5-9 ticks (minor ticks in C) | only circles clear of their colour's cluster; all at ln of a whole number |
| S1 | `figs1_red`, `_blue`, `_brown`, `_magenta`, `_green` (`flow_9EG7_*`), 11-18 intensities each | y 5 labelled ticks (the unlabelled one at the axis left out), misfit 2.7 px; x log, fitted on the 4 decade ticks, misfit 2.2 px | `figures/_s1.py`: a raster image; each line found by its colour; interval covers the line over 3 px either side because the minor ticks sit up to 9 px from log10(2..9); intensities where a line is covered by another are not read |

The Fig. S1 overlay marks are drawn in the same magenta as the Mn2+ line, so they cannot be seen on
it; that line's values were checked against the drawn curve (peak about 0.0196 near 10^2).

All 42 readings were checked with `boxgraph figure check`; every mark sits on the bar top, square or
ring meant (for Fig. S5 the four series of a panel were also overlaid in one image). The bar values
fall on round numbers (0.07, 0.12, 0.22, ...), as plotted means of 100-contact counts should, and the
Fig. S5 circles at ln 1, ln 2, ln 3, ..., which checks the calibration independently.

What the readings show for the open questions:

- `q_s5_not_read`: Fig. S5 is now read in part (`q_s5_tails_read`); it still feeds no run.
- `q_measured_plots_left_out`: answered; the plots it lists are read, except Fig. S3 B (below). The
  three lifetimes the text gives for Fig. S3 C (0.3, 2.8, 10 s) are recorded and compared with the bar
  labels (0.3, 2.8, 13.4); the third differs (`q_s3c_third_bin_lifetime`).
- Fig. 2 shows three specific adhesion frequencies above the 20% the text says was kept
  (`q_fig2_binding_above_20pc`).
- The BSA rupture-force histogram (Fig. S2 A) puts about 0.82 of its events below 20 pN, which agrees
  with the text's "most of these events were ruptured at forces <20 pN" (p. 3).

## Left out

- The grey Fc/GG-7 squares where they are redrawn (Figs. 3 B-C, 5, 6): the same curve as Fig. 3 A,
  partly covered by the black series.
- Fig. 1 (schematic and example force traces), Figs. 3 E-F, 4 and 5 D, 6 D schematics: drawings.
- Fig. S3 A: three single example force-extension traces (single random trajectories).
- Fig. S3 B: a cloud of about 250 single events (open squares on a log lifetime axis), many
  overlapping, so single squares cannot be told apart reliably; its summary, Fig. S3 C, is read.
- Fig. S5: the dense stacks of circles at short lifetimes in every series (see above).
- Fig. S1: the positions where one curve is drawn under another (no pixel of its colour there).
