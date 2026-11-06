# Figures of formaggia2003

All plots in this paper are embedded low-resolution rasters (black lines on white). Each reading
renders one panel at 900 dpi and runs its own code (`figures/<id>.py`, shared method in
`figures/_fig.py`): the plot box and its inward tick marks are found in the image, the printed tick
labels are matched to evenly spaced ticks (and to the box corners where a label is printed there),
and the chosen line is taken as one of the separate tracks of ink in each column.

## Read

| Figure | Panels | Readings |
|---|---|---|
| Fig. 6 (p. 15), middle of Omega_1 | A, W1, W2 | `f6_A_dotted`, `f6_A_dashed` (dashed and dash-dot coincide), `f6_W1` (all coincide), `f6_W2_dotted`, `f6_W2_dashed`, `f6_W2_dashdot` |
| Fig. 7 (p. 16), middle of Omega_2 | A, W1, W2 | `f7_A_dotted`, `f7_A_dashed`, `f7_W1_dotted`, `f7_W1_dashed` (dashed and dash-dot coincide), `f7_W2` (all coincide) |
| Fig. 8 (p. 16), middle of Omega_3 | A, W1, W2 | `f8_A_top` (dotted and dashed coincide), `f8_A_dashdot`, `f8_W1_top`, `f8_W1_dashdot`, `f8_W2` (all coincide) |
| Fig. 11 (p. 17), middle of Omega_1 | A, W1, W2 | `f11_A`, `f11_W1`, `f11_W2` |
| Fig. 12 (p. 18), middle of Omega_2 | A, W1, W2 | `f12_A`, `f12_W1`, `f12_W2` |
| Fig. 13 (p. 18), middle of Omega_6 | A, W1, W2 | `f13_A`, `f13_W1`, `f13_W2` |

Figs. 6-8 are read at t = 0.005, 0.015, ..., 0.175 s; Figs. 11-13 at t = 0.05, 0.15, ..., 1.95 s (as
labelled). Where lines coincide, one track holds them all and its interval covers them.

Notes on the readings:
- Fig. 7, area panel: the label at the top of the axis reads 0.58 but the ticks (0.5, 0.52, 0.54)
  put the top at 0.56; the calibration uses the ticks and the 0.5 at the bottom corner, not the 0.58
  label (question `q_fig7_axis_label`).
- Fig. 6 W2: the dashed and dash-dot lines run within a few cm/s of each other; where they separate
  (three tracks) the dashed line is the middle one, elsewhere the reading covers both.

## Section 4 (Figs. 14-18), read in a second pass

The spatial profiles of the extended wall models (wall inertia, viscoelasticity, longitudinal
pre-stress). No model in this record produces them (the paper does not give enough inputs to run
them, `q_wall_models_not_run`), so they are recorded as predicted data with no run or comparison: a
later model may predict them. Each reading uses `figures/_s4.py` with the same calibration as above
(box, inward ticks matched to the printed labels and the corners, largest misfit added to every
interval; the largest misfits were 2.9 px on an x axis and 3.1 px on a y axis, against plot boxes of
about 2100 x 700 px) at 900 dpi. The x axis is
the axial position z (cm). Where two lines share a panel (dotted 'without' and continuous 'with'
the extra term), they are told apart by shape: the ink is eroded so that touching dots come apart,
dot-shaped pieces are the dotted line, the rest the continuous line. A dotted value is interpolated
between the dots on either side; where the dots run as unbroken ink (on the continuous line or in a
chain) the value is read on that ink, on the track a written rule names where two tracks run a few
pixels apart. A continuous-line value is the track farthest from the dotted line where there are
two. Every overlay in `figwork/<id>.png` was looked at; rules were added wherever a cross sat on the
wrong line.

| Panel | Reading | Curve, positions |
|---|---|---|
| Fig. 14 (p. 20) top left, A at t = 0 | `f14_A_t0` | single line; z = 5..155 by 5, and by 0.5 about the feet (60-67, 93-100 cm) |
| Fig. 14 top left, Q at t = 0 | `f14_Q_t0` | single (zero) line; z = 5..155 by 5 |
| Fig. 14 top right, A and Q without inertia, t = 0.05 s | `f14_A_noin`, `f14_Q_noin` | single line; z = 5..155 by 5 |
| Fig. 14 bottom left, A and Q with inertia, t = 0.05 s | `f14_A_in`, `f14_Q_in` | single line; z = 5..155 by 5 |
| Fig. 14 bottom right, difference in area (x 10^-3) | `f14_dA`, `f14_dA_ext` | the line where it does not oscillate (25, 30, 60, 100, 130, 135 cm left out: near-vertical oscillations); `_ext`: its highest and lowest ink |
| Fig. 14 bottom right, difference in flow | `f14_dQ`, `f14_dQ_ext` | as above (25, 60, 100, 130, 135 cm left out) |
| Fig. 15 (p. 21) top left, A and Q at t = 0 | `f15_A_t0`, `f15_Q_t0` | single line; z = 0.5..19.5 by 0.5 |
| Fig. 15, A and Q at t = 0.005, 0.010, 0.015 s | `f15_A005_noin`, `f15_A005_in`, `f15_Q005_noin`, `f15_Q005_in`, and the same for 010 and 015 | dotted (without inertia) and continuous (wall density 1); z = 0.5..19.5 by 0.5. The two lines lie within a few pixels nearly everywhere, so both readings often take the same ink and their intervals cover both |
| Fig. 16 (p. 22) top left, A at t = 0 | `f16_A_t0` | single line; z = 0.5..19.5 by 0.5 |
| Fig. 16, A and Q at t = 0.005, 0.010, 0.015 s | `f16_A005_noin`, `f16_A005_in`, ... `f16_Q015_in` | dotted (without inertia) and continuous (wall density 100), well apart; z = 0.5..19.5 by 0.5 |
| Fig. 17 (p. 23) top, A without the viscoelastic term | `f17_A_long` (left, z to 120 cm), `f17_A_short` (right, z to 10 cm) | single line; left z = 5..115 by 5 (calibrated on the right-hand ticks: the curve meets the left border), right z = 0.25..9.75 by 0.25 |
| Fig. 17 bottom, difference in area | `f17_dA_long` (x 10^-4), `f17_dA_short` (x 10^-3), `f17_dA_long_ext`, `f17_dA_short_ext` | single line, and its highest and lowest ink |
| Fig. 18 (p. 24), A at t = 0.1 and 0.2 s | `f18_A01_noprestress`, `f18_A02_noprestress` | continuous line (without the longitudinal term), z = 0.25..14.75 by 0.25 except at the two near-vertical jumps (4.75-5 and 10-10.25 cm) |
| Fig. 18, A at t = 0.1 and 0.2 s | `f18_A01_prestress`, `f18_A02_prestress` | dotted line (with the pre-stress term): fine, faint dots, read without erosion; z = 0.25..14.75 by 0.25 (one position on the t = 0.1 s jump read with a wide interval) |

What the readings settle (new questions, the old ones unchanged):
- `q_fig14_wavelength_figure`: the initial half-sine of Fig. 14 is about 32-33 cm long (feet near 64
  and 96 cm), as the text says (32 cm), not the caption's 35 cm (`q_fig14_wavelength`).
- `q_wall_claims_figures`: the plotted differences are of the order the text claims (a few 10^-3
  relative in Fig. 14, under 0.5% in Fig. 17); a reading of the plots, not a check of the simulations.
- `q_fig17_panels`: both panels of Fig. 17 are titled t = 0.2 s; the right panel's short pulse at
  z = 2-8 cm cannot have travelled for 0.2 s.

Notes:
- The extremes readings (`_ext`) give the outer edge of the ink, so they overstate the peak by up to
  half a line width; their interval is one raster pixel plus the calibration misfit.
- Fig. 18: the continuous line is drawn as a near-vertical jump at z = 5 and 10 cm, and the text says
  the dotted line smooths it 'with a jump ... of the same magnitude'; the readings on either side of
  the jumps show this (e.g. at t = 0.1 s, 0.860 to 0.792 cm^2 across z = 5 cm on both lines).

## Left out

- Figs. 1-5, 9 and 10: drawings and a photograph (geometry, endograft, domain decomposition), no values.
- Fig. 16, top left, Q at t = 0: the flat zero line is drawn as heavily as the box and sits on the
  0 tick, so the plot box and ticks cannot be calibrated from the image; it is the same zero line as
  Fig. 15's, which is read (`f15_Q_t0`).
- The oscillating stretches of the Fig. 14 difference panels (see above): the line is near-vertical
  there and no single value can be read at a given z; the extremes readings cover their size.
