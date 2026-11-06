# Figures of westerhof2009

Every plot with values is read by code from the page (`figures/*.py`; `_fig4.py`, `_fig6.py` and `_fig8.py`
hold the shared calibration and tracing). The figures are vector art, so lines are crisp; intervals come from
line width, calibration misfit, and the places where one line covers another. All plotted data are adapted
from cited works (from_source on each datum). The review prints none of the parameters behind its plotted
windkessel curves, so no run or comparison is made for them: they are recorded as predicted curves for a
later job that has those parameters (from refs 76 and 39) or fits them.

- **Fig. 1, Fig. 5**: drawings, no values. Fig. 5's circuits are what the windkessel impedance models are
  built from.
- **Fig. 2** (Randall et al. [46]): left out. It shows pressure and flow traces with a vertical scale (100 mmHg,
  100 ml/s) but no time axis or time scale, and the middle stretch is a solid block of overlapping beats.
  There is no x to index a reading by.
- **Fig. 3**: left out. It is a schematic waveform with no values on either axis.
- **Fig. 4, modulus** (p. 3, Westerhof et al. [76]): read at 1200 dpi. The crop holds both panels. The x axis
  comes from the modulus panel's 7 ticks (0-12 Hz, misfit 2.3 px, about 0.02 Hz). The y axis comes from 6
  ticks (0-1.0 mmHg/(ml/s), misfit 0.9 px). There are four readings:
  `fig4_mod_measured` (grey line), `fig4_mod_wk2` (dotted), `fig4_mod_wk3` (dashed) and `fig4_mod_wk4`
  (solid). The black lines are told apart by the length of their pieces. Positions where the lines overlap
  (below about 1.5 Hz, and dashed against solid above 8.5 Hz) are left out of `at`. The Zc arrow is an
  annotation and is not read.
- **Fig. 4, phase**: the phase panel has no frequency labels of its own, so its x calibration comes from the
  modulus panel's ticks (same origin column, curves end in the same column). The y axis comes from 3 ticks
  (0, -40, -80 deg, misfit 0.7 px). There are four readings: `fig4_ph_measured`, `fig4_ph_wk2`, `fig4_ph_wk3`
  and `fig4_ph_wk4`. Above 11 Hz the measured grey line runs along the black zero line; there its centre is
  taken midway between the edges that show, and the interval covers the zero line.
  The dotted (two-element) phase reads close to -89 deg at 12 Hz. That bears on q_wk2_limit_inputs, whose
  added-input run gives about -89 deg at 12 Hz.
- **Fig. 6, pressure** (p. 4, Murgo et al. [39]): read at 1800 dpi. There are four readings: `fig6_pA_black`,
  `fig6_pA_grey`, `fig6_pC_black` and `fig6_pC_grey`. The x axis uses 11 ticks per panel (0-1.0 s, misfit
  0.7 px). The y axis uses the type A panel's 7 ticks (60-120 mmHg, misfit 0.5 px). Only the type A axis
  is labelled, and the type C panel's own ticks at 80 and 70 mmHg are off even spacing by about 38 and
  20 px, so the type C pressures use the type A scale; the two axes span the same rows to within 5 px. The
  panel titles are excluded as black ink lying wholly above 110 mmHg. Which line is measured and which is
  derived is not stated (q_fig6_line_identity).
- **Fig. 6, impedance modulus and phase**: read at 2400 dpi, one crop per beat type with both panels. Each
  panel is calibrated on its own axis. The y ticks are 200/100/0 (type A modulus), 100/50/0 (type C modulus)
  and 50/0/-50 (phase), with misfit at most 2.5 px. The modulus x axis has its own ticks at 0, 5 and 10 Hz.
  The phase x axis has ticks at 5 and 10 Hz, and 0 Hz is taken where its y axis meets it (misfit at most
  3.1 px, about 0.01 Hz). In type C the two panels' frequency axes are offset by about 0.3 Hz, and the
  crosses follow each panel's own axis.
  - The data readings are `fig6_A_mod_data`, `fig6_A_ph_data` (10 points each), `fig6_C_mod_data` and
    `fig6_C_ph_data` (9 points each). The crosses are a dark-grey ink of their own, distinct from the black
    line and the light-grey windkessel line. The point is where the horizontal and vertical bars cross. The
    vertical bar is the error bar (unstated; q_fig6_bars). Where the light-grey line covers an end of a bar
    or part of a horizontal bar, the outer bound or interval is widened and the note says so.
  - Two points need their own handling. In the type C modulus panel, the first point's horizontal tick is
    under the grey line, so that point is taken at its bar's middle with a wider interval. A lone dash at
    about 11.9 Hz has no vertical bar and lies within the previous cross's horizontal bar, so it is not
    taken as a point.
  - The windkessel readings are `fig6_A_mod_wk3`, `fig6_A_ph_wk3`, `fig6_C_mod_wk3` and `fig6_C_ph_wk3`
    (the light-grey line).
  The gap between the measured and windkessel phase near 10 Hz is the effect that the 8 ms time-delay
  remark on p. 4 addresses (about 30 deg at 10 Hz; q_delay_approximate). These readings let a later job
  compare the two.
- **Fig. 7**: left out. It is a drawing of the isolated-heart set-up. Its inset is a small sketch of
  pressure and flow traces with only partial scales (100 mmHg, 10 ml/s, 1 s) and no axes to calibrate a
  time course.
- **Fig. 8** (p. 6, Elzinga and Westerhof [15]): read at 1200 dpi. There are 3 x 3 panels of single-beat
  pressure (thick line) and flow (thin line), with no time axis but scale brackets of 0-100 mmHg and
  0-10 ml/s. Per row of panels (R = 22, 46, 103), three readings give one point per panel, with x the
  column's C label (57, 19, 4.8 x 10^-3 ml/mmHg):
  - `fig8_R*_pmax`: the highest pressure;
  - `fig8_R*_pmin`: the lowest pressure;
  - `fig8_R*_qmax`: the highest flow.

  The scales come from the brackets' end ticks (two marks each, so there is no misfit). The 0 mmHg tick
  lies 4.5 px above the top row's bottom edge, and that offset is carried to the other rows, as the flow
  zero is from the bottom row (q_fig8_scales). The two traces are told apart by line width: pixels 9.5 px
  wide or more within 3 px count as pressure. Where a flow peak touches the pressure line (the C = 4.8
  column), its interval is widened. These are the measurements the text cites as supporting the Table 2
  sensitivities ("These predictions are supported by experimental data of (see Fig. 8)"). No model in the
  record produces them; a later paper's heart-plus-windkessel model may.
- **Fig. 8, R and C labels**: recorded earlier as reported data (fig8_r_*, fig8_c_*), unchanged.
