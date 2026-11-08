# Figures in schwarz2020

Every plot of data in Figs. 2-6 is read with calibrated code readings (`figures.yaml`, mode `code`).
The figures are vector art, rendered at 600-1000 dpi. Shared code is in `figures/_f5.py` for Fig. 5 and
in `figures/_sz.py` and `figures/_boxfigs.py` for the box plots and histograms. Each reading file names
its curve or statistic. Every axis is calibrated from its own tick marks, found as ink going outward
from the axis line and matched to the printed labels. The misfit is the largest distance of a matched
tick from the least-squares axis line, and on logarithmic axes it includes the check of the minor
ticks against the decade pattern. Every overlay in `figwork/` was inspected: the marks sit on the
intended line, area edge, box feature or bar top.

## Read

- **Fig. 1** (p. 3): left out. These are images and reconstructions (micrographs, MIPs, 3D renderings), and none has values to read.
- **Fig. 2A** (p. 6): `f2a_hist`, the segment-length histogram (number of segments per 1 mm bin, log
  axis), read at the 22 bin centres. Calibration: all 23 x ticks = 0 ... 22 mm, and the 7 long y ticks =
  1 ... 1,000,000. Misfit under 1 px; the bars for 4, 3 and 2 segments read 3.97, 2.99 and 1.99.
  Bins 16-21 mm have no bar above the axis (on a log axis an empty bin cannot be drawn) and are not
  read. The read bins add up to within about 0.2% of the 202,184 segments of Table 1. Origin: measured.
- **Fig. 2B** (p. 6): `f2b_whisker_lo`, `f2b_q1`, `f2b_median`, `f2b_q3`, `f2b_whisker_hi`. These are the box plots of
  segment length per diameter class, x = class lower bound. Calibration: the first seven x ticks =
  0, 0.5, ..., 3 mm (the axis is broken after 3). The upper whisker of the >= 400 um class ends beyond the
  break, so it is not read. Per the caption, whiskers are 1.5 IQR. Origin: measured.
- **Fig. 3A** (p. 7): `f3a_*` (five statistics) for daughter symmetry per mother class. The x ticks are
  all 21 ticks, 0 ... 1 by 0.05; each value's note gives the misfit. The upper whiskers end at 1. Origin: measured. The >= 400 um median reads
  about 0.59 (q_fig3a_fig4_large_class).
- **Figs. 3B, 3C** (p. 7): `f3b_hist` (75-90 um) and `f3c_hist` (>= 400 um), the symmetry histograms with bins
  of 0.05. Calibration: 11 x ticks = 0 ... 1, 8 long y ticks = 0 ... 0.14. In 3B the bins below 0.25 have
  no bar above the axis line and are not read. Both sets of read bars add up to 1.00. Origin: measured.
- **Fig. 4** (p. 8): `f4_symhi_*` (daughter symmetry 0.5-1.0, light boxes) and `f4_symlo_*` (0.0-0.5, dark
  boxes), five statistics each, x = mother class lower bound. The left panel (30-75 um) has its own
  axis 0 ... 60 and the right panel 0 ... 3; each is calibrated from its long ticks. The light box of
  30-45 um shows no median line, so that median is not read. Lower whisker ends that run into the
  x axis (>= 400 um) have intervals reaching across the axis line. Origin: measured. No model in the record
  predicts these per class: the linear area-growth fit needs one symmetry value, and the boxes are
  symmetry ranges.
- **Fig. 5A** (p. 9): `f5a_fit` (black 'cast, fit'), `f5a_cast` (brown median, read only where it is not
  hidden under the black line), and `f5a_insilico` (teal median). Calibration: 5 long x ticks = 1 ... 10^4 um
  and 8 long y ticks = 10^-6 ... 10^1; misfit 0.9 px, and minor ticks off the decade pattern by at most 1 px.
  The IQR areas are thin and lie mostly under the lines, so they are not read. Runs and comparisons:
  the heart law with the p. 7 exponent (-2.22) does **not** reproduce the fit line, and with the
  p. 12 exponent (2.22) it **does** (cmp_f5a_fit_printed, cmp_f5a_fit_p12; settles q_G_exponent_sign
  towards a misprinted sign, q_fig5a_exponent_sign). The heart law is close to the brown median
  (cmp_f5a_cast_p12). The in silico law, stated for larger vessels, is set against the whole in silico
  median (cmp_f5a_insilico).
- **Fig. 5B** (p. 9): `f5b_fit`, `f5b_cast`, `f5b_insilico`, the edges of the brown area (`f5b_cast_q1`, `f5b_cast_q3`)
  and of the teal area (`f5b_insilico_q1`, `f5b_insilico_q3`). Long y ticks = 20 ... 90 mmHg, misfit 0.9 px. The pressure
  law reproduces the fit line (cmp_f5b_fit). The median at 100 um reads about 28 mmHg, about 32% of 90
  (q_fig5b_pressure_100um).
- **Fig. 5C** (p. 9): `f5c_fit`, `f5c_cast`, `f5c_insilico`, `f5c_cast_q1`, `f5c_cast_q3`. Every decade on the y axis
  has a long tick (10^-7 ... 10^3, labels every second decade); misfit 0.6 px. The flow law reproduces
  the fit line (cmp_f5c_fit) but not the heart median (cmp_f5c_cast; the median lies below it up to
  about 500 um, by a factor of about 3 at 100 um), which explains the printed '3,000-times' (q_fig5c_flow_ratio). The teal area is
  narrow and under the line, so it is not read.
- **Fig. 5D** (p. 9): `f5d_fit`, `f5d_cast`, `f5d_insilico`, `f5d_cast_q1`, `f5d_cast_q3`. Long y ticks = 0 ... 140
  cm/s, misfit 0.7 px. The y axis says 'Peak velocity' and the caption says centerline velocity. The fit line
  is hidden between about 60 and 150 um, where all lines lie near zero. The velocity law reproduces the
  fit line (cmp_f5d_fit) but not the median (cmp_f5d_cast). The velocity implied by the flow law under
  Poiseuille flow is not reproduced either (cmp_f5d_cast_from_flow; q_velocity_flow_laws). The top of the
  brown area is flat at about 122-123 cm/s above 2.5 mm, as drawn. The teal area is narrow and is not read.
- **Fig. 5E** (p. 9): `f5e_cast`, `f5e_insilico`, `f5e_cast_q1`, `f5e_cast_q3`, `f5e_insilico_q1`, `f5e_insilico_q3`.
  Long y ticks = 0 ... 20 Pa, misfit 0.7 px. The plateau near 5 Pa below 300 um and the peak near 630 um
  are in the reading (q_fig5e_wall_shear). No run: wall shear stress needs the network flows, and the
  record's single-diameter route (cmp_wss_100um) is kept as it was.
- **Fig. 6** (p. 10): `f6_*` (five statistics), perfusion box plots per region, x = region index 1-6 (LV epi,
  LV mid, LV endo, Sept LV, Sept mid, Sept RV). Long y ticks = 0 ... 30 ml/min/g. The lower whiskers of
  regions 1-3 run into the x axis (intervals across it). The region medians (about 1.5-7.4) bracket the
  overall median of 5.6 ml/min/g printed in the text. Origin: predicted (network output).

## Not compared, and why

The Fig. 5 medians and IQR edges other than those above, and the Fig. 6 statistics, are outputs of the
network hemodynamics. That model is not runnable from the paper (q_network_data), and the validator
warns that they are never compared. They are recorded for a run on the released network (schwarz_data).
The measured distributions of Figs. 2-4 have no predicting model in this record and are recorded for
models in other papers.

## Earlier pass

No figure was read before this pass (the earlier session could not render pages). The figures that
the first pass listed for a later reading are all read above.
