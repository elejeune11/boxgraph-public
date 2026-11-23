# Figures of panzetta2019

Two passes. The first read the model curves (Figs. 9 and S13) with `figures/_fig.py`. The second
(this update) reads every plot of measured data, which the first pass had left out, with
`figures/_exp.py`, and the stress-strain lines of Fig. S1 with `_fig.py`. Every reading was run with
`boxgraph figure check` (overlays in `figwork/<reading id>.png`), and the magenta marks were checked
against the curve, bar or error bar meant.

## Model curves (first pass, unchanged)

The model results of the paper are only plotted: Fig. 9 (p. 8) and Fig. S13 (p. 23). Both are raster
images of Excel charts without tick marks. They are read by the record's own code (`figures/_fig.py`,
one stub per series):

- the axes are calibrated from the centres of the printed labels (Excel centres each label on its value),
  matched in order to the labels typed in each stub, with a linear or log10 fit and its misfit (S13 about
  1.2-1.9 px at 1200 dpi; Fig. 9 about 1.3-2.1 px). The second pass found, on Fig. 3A, which has both
  labels and tick marks, that label centres sit about 9 px (1200 dpi) below their ticks. If Figs. 9 and
  S13 carry the same offset, their readings are biased by about 9 px, which is more than their stated misfit.
- a series is the pixels nearest its colour; Fig. S13's markers are kept as blobs of at least 150 px (the
  antialiased rims of other markers are smaller); Fig. 9's lines are traced by continuity, so that pixels of
  a neighbouring line or of the black x0 arrow are not followed;
- at each x the value is the centre of the series' pixels within 2 px, or an interpolation between the nearest
  columns on either side (markers are spaced; the arrow hides part of the Fig. 9 green line); the 95%
  interval adds half the marker or line extent, half the interpolated jump, the y misfit, one pixel and the
  slope times the x misfit. On the steep, stiff side the stacked markers make the intervals wide.

| reading | figure | series |
|---|---|---|
| figS13l_all | Fig. S13 left (canonical model) | blue, purple and green together: one curve |
| figS13r_blue / _purple / _green | Fig. S13 right (modified model) | the three x0, each over the ks it covers |
| fig9r_blue / _purple / _green | Fig. 9 right | flow against ks, 5-195 pN/nm |
| fig9r_*_at_s13 | Fig. 9 right | the same curves at the x positions of the S13 series, for the consistency comparisons |
| fig9l_blue / _purple / _green | Fig. 9 left | flow against nc, 400-3500 |

The Fig. S13 markers below ks = 5 pN/nm (at 0.1, 1.2, 2.3 and 3.4 pN/nm) are too sparse to interpolate
on a log axis, so they are not read. Fig. 9 (left) is not read below nc = 400, where the curves leave the
top of the plot.

## Measured data (second pass)

None of these is predicted by a model of this record: the clutch model gives an actin flow, not an
intracellular MSD, cell area or shape. They are recorded (origin `measured`) for models of other papers.
Error bars are SEM: the caption of each main-text figure and of Figs. S7 and S8 says so. Figs. S3, S4,
S5 and S10 say nothing, and the Methods' "Data are reported as mean ± SEM" (p. 9) is cited for them.

How `_exp.py` reads (its docstring has the details):
- **MSD panels** (log-log, 0.1-10 s by 10^-5-10^-2 um^2): the axes come from the spine ends, which Excel
  draws from the axis minimum to its maximum. They are checked against the small tick marks at the inner
  decades; residuals are 0.2-5.7 px against about 420 px per decade at 1200 dpi, and the misfit is at least
  2 px. On a few panels (Fig. 4A right, B.2 top and bottom) no tick mark was found, so the check rests on
  the spine ends alone. Each line is traced by colour and continuity (at most 8 px of jump per column) and
  read at 0.15, 0.2, 0.3, 0.5, 0.7, 1, 1.5, 2, 3 and 4 s.
- **Bars**: the y axis comes from the tick marks where the chart has them (Fig. 3, misfit about 1 px) or from
  the label centres plus a 9 px allowance (see above). Bars are indexed 1, 2, ... from left to right, and
  each reading's `what` says which condition each index is. The value is the top edge (the outline's centre
  where there is one; hatching is bridged by averaging). The error bar's stem is the longest run of ink
  going up from the top edge. Its lower half is read inside pale bars and inside dark bars where it is black;
  where it is hidden, the lower end is the mirror of the upper. Where the two halves read differ by more than
  4 px and 25% (Fig. 6L bar 2, Fig. S8 nuclei bar 3, Fig. 7G bar 1, a few others), the outer interval covers
  the longer half on both sides.
- **Histograms** (Fig. S9): x is calibrated from the bin-edge labels, y from the count labels, and each bin
  is read at its centre. The counts come out within 0.1 of integers.

Bullets, panel by panel:

- **Fig. 1** (p. 2), **Fig. 8** (p. 7), **S2** (p. 12), **S11, S12** (p. 22): drawings, left out.
- **Fig. 2 A.1, B.1** (p. 3): drawings, left out. **A.2, B.2, B.3**: read, six panels with three lines each
  (blue 0%, purple 6%, green 9%): `f2_{a2,b2,b3}_{balb,mc3t3}_{0,6,9}`, 18 readings at 1200 dpi. Tick
  residuals are at most 3.8 px. The 0% curve is the same in A.2, B.2 and B.3 within the readings.
- **Fig. 3** (p. 4): read, four bar charts of the MSD at 1 s with SEM bars. `f3a_balb`, `f3a_mc3t3` (seven
  bars each) and `f3b_balb`, `f3b_mc3t3` (four each) are calibrated on the tick marks. Thirteen of the
  fourteen bars of Fig. 3A equal their Fig. 2 curve at 1 s; the exception is in q_fig3a_vs_fig2a2_balb6.
- **Fig. 4** (p. 5): read, six panels with two lines each (blue 0%, green 9%): `f4_{a,b1,b2}_{balb,mc3t3}_{0,9}`,
  12 readings. Tick residuals are at most 5.7 px (B.1 top).
- **Fig. 5** (p. 6, right): read, four lines: `f5_0`, `f5_6`, `f5_9`, `f5_6to9` at 1600 dpi (a small panel).
  The red line hides the green one over 0.12-0.6 s, so `f5_9` is read without tracing, and its `at` list
  leaves out 0.15, 0.3 and 0.5 s, where the red line covers it. The left of the figure is a drawing. The blue, purple
  and green curves coincide with Fig. 2 A.2 (left), not with B.2 as the caption implies (q_fig5_condition).
- **Fig. 6** (p. 6): A-F are micrographs, left out. G-L are read, three bars each with SEM: `f6g` to `f6l`
  (spreading area, shape factor and nuclear area for BALB/3T3 and MC3T3 on PDMS), label-calibrated
  (misfit 1.3-2.3 px plus 9 px).
- **Fig. 7** (p. 7): A-D are micrographs, left out. E-J are read, two bars each: `f7e` to `f7j` (the same
  quantities on PU).
- **Fig. 9, Fig. S13**: first pass, above.
- **Fig. S1** (p. 11): read. `s1_pdms_fit` is the red line of the left panel, the legend's fit y = 930.32x.
  The measured average curve lies under it and shows only at the two ends, so it cannot be read. `s1_pu_fit`
  is the red line of the right panel (log-log), with legend y = 185.07x. Both are label-calibrated by `_fig.py`;
  on the right, "0.1" sits on the first x label and is left out. Runs of the printed equations against the
  lines (`cmp_s1_pdms_line`, `cmp_s1_pu_line`), the printed moduli against each other (930.32 kPa, 930 kPa,
  1 MPa), and PU's 0.6 MPa against 2(1 + nu) x 185.07 kPa with an added nu (`cmp_pu_youngs`, a reconstructed
  step that the paper does not state).
- **Fig. S3** (p. 13): read, the radius of gyration, four bar charts: `s3a_balb`, `s3a_mc3t3` (seven bars),
  `s3b_balb`, `s3b_mc3t3` (four). Label-calibrated at 600 dpi. In two panels the "0" label merges with the
  x labels and is left out of the fit.
- **Fig. S4, S5** (pp. 15-16): read. The MSD curves are `s4_msd_0/9` and `s5_msd_0/9` (log-log, 600 dpi),
  and the bars of the MSD at 1 s are `s4_bar` and `s5_bar` (x10^-4 axes).
- **Fig. S6** (p. 17): read, three lines: `s6_0`, `s6_3post` (orange) and `s6_3_2h` (red). They overlap
  almost everywhere. Positions where one line hides another by more than 40 px are left out of the `at`
  lists (`s6_0` at 0.15 and 0.2 s, `s6_3post` at 1.5 s).
- **Fig. S7, S8** (pp. 18-19): the micrographs are left out. The bar charts are read: `s7_spread`,
  `s7_nuclei`, `s8_spread`, `s8_nuclei`, three bars each, including the hatched one (q_s7_caption_vs_legend).
- **Fig. S9** (p. 20): read, six orientation histograms: `s9a_0`, `s9a_9pre`, `s9a_9post`, `s9b_0`,
  `s9b_9pre`, `s9b_9post`. The bins are 30 degrees wide and read at their centres. There are no error bars.
- **Fig. S10** (p. 21): read, `s10_afm`, four bars (BALB/3T3 and MC3T3 at 0% and 9%) of the cells' AFM
  Young's modulus with their error bars.

## What the readings settle

- **q_fig9_vs_S13** and the first pass's comparisons are unchanged. The second pass adds only the
  calibration caveat above: the label centres may be offset by about 9 px.
- **New questions from the measured data**: q_fig3a_vs_fig2a2_balb6 (one Fig. 3 bar disagrees with its
  Fig. 2 curve), q_fold_changes (the printed fold decreases against the curves), q_fig5_condition (which
  condition Fig. 5 shows) and q_s7_caption_vs_legend.
- **None of these measurements tests the clutch model of this record.** The paper links its experiments
  to the model only qualitatively (stiffening with stretch), and it gives no conversion from substrate strain
  to x0 (q_x0_strain).
