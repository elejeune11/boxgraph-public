# Figures of stergiopulos1999

Figure pass of 2026-11-02. The first reading read no figure (its page-rendering commands were refused). Every
panel that plots values is now read by calibrated code in `figures/`, checked with `boxgraph figure check` (magenta
marks on the intended line, bar top or square). All figures are scans, nearly black and white; crops are rendered
at 1200 dpi. Shared methods are in `figures/_waves.py` (Figs. 1, 3, 4), `figures/_fig2.py` (Fig. 2) and
`figures/_fig5.py` (Fig. 5). Their docstrings say how the axes are calibrated and how the intervals are formed.
Each reading lists in `at` only the positions its code can read alone. Positions where two lines merge are refused
by the code and left out.

- **Fig. 1, top (p. 3), windkessel schematics.** Left out: a drawing with no values. The models are `zin_3wk`
  and `zin_4wk`.
- **Fig. 1, middle left, dog 71 aortic flow (measured).** Read as `fig1_flow_d71` (datum `fig1_flow_d71_fig`,
  44 points, 0.01-0.44 s). The thick line is kept by a 15 px disk opening. x is calibrated from the frame lines
  (0, 0.5) and four inner ticks; y from the frame lines (120, -40) and three inner ticks on the right frame. Misfit
  is 2.2 px in x and 1.9 px in y. The labels 0.1-0.5 are printed only under the panel below; it shares the same
  columns.
- **Fig. 1, middle right.** Left out: the same flow wave as the middle-left panel.
- **Fig. 1, bottom left, dog 71 pressure.** Measured (thick): `fig1_p_d71_meas`, 39 of 44 points. Three-element
  fit (thin): `fig1_p_d71_3wk`, 33 points. Calibration is as above, with labels 120/100/80/60. Misfit is 5.2 px in
  x (a scan distortion) and 3.0 px in y; both widen every interval.
- **Fig. 1, bottom right.** Four-element fit (thin): `fig1_p_d71_4wk`, 17 points. The fit lies on the measured
  line for most of the beat and is refused there. The measured line repeats the bottom-left panel and is not read
  again. No model in the record produces these waves (question `q_waves_model`).
- **Fig. 2, top and bottom (p. 4), dog averages ± SE of Z_c and C.** Each bar is read twice:
  `fig2_<bar>_mean` gives the bar height with its SE bar, and `fig2_<bar>_se` gives the length of the upper SE bar.
  The bars are `rc_std`, `rc_3wk`, `rc_4wk`, `c_ppm`, `c_ar`, `c_3wk` and `c_4wk`. Calibration uses the outward
  y ticks every 0.05, matched to the labels 0.0-0.4 (top) and 0.0-0.3 (bottom). Misfit is 2.8 px (top) and 4.3 px
  (bottom). The lower half of each error bar is hidden inside the bar and taken as the mirror of the upper half;
  the caption says the bars are SE.
  - New processing models `mean_se_rc` and `mean_se_c` compute the mean and SE of the seven Table 1 values.
  - All 14 consistency comparisons are reproduced. Fig. 2 agrees with Table 1 in mean and SE for every bar.
  - The asterisks (on 3-el Z_c, 4-el Z_c and 3-el C, not on 4-el C) agree with the printed P values (0.0014,
    0.031, 0.0029, 0.81).
- **Fig. 3 (p. 4), dog 71 pressure predicted with standard Z_c and C.** Three-element windkessel (dotted):
  `fig3_p_3wk_std`, 32 points. Four-element windkessel (thin solid): `fig3_p_4wk_std`, 21 points. Misfit is 1.8 px
  in x and 1.4 px in y. The measured (thick) line repeats Fig. 1 and is not read again. No runnable model drives a
  windkessel with a flow wave (`q_waves_model`).
- **Fig. 4A (p. 5), human aortic flow (measured, ref. 12).** Read as `fig4a_flow_A` (42 points, 0-0.82 s) and
  `fig4a_flow_C` (39 points, 0-0.76 s). x is calibrated from the five ticks labelled 0-0.8 (the frame is not on a
  label), with a misfit of 4.2 px. y uses the frame lines (800, -200) and four ticks.
- **Fig. 4B, human aortic pressure (measured).** Read as `fig4b_p_A` (41 points) and `fig4b_p_C` (38 points).
- **Fig. 4C and 4D, three- and four-element windkessel fits (thin lines).** Read as `fig4c_p_3wk_A` (31 points),
  `fig4c_p_3wk_C` (22), `fig4d_p_4wk_A` (26) and `fig4d_p_4wk_C` (15). The measured lines repeat Fig. 4B and are not
  read again. The legend box is blanked.
- **Fig. 5 (p. 6), dog 71 input impedance.** Measured squares: `fig5_mod_measured` and `fig5_ph_measured`, five
  harmonics each; the 0 Hz square, phase 0 by definition, is not read. Dotted line: `fig5_mod_dotted` and
  `fig5_ph_dotted`. Solid line: `fig5_mod_solid` and `fig5_ph_solid`; each curve has 22-24 points, 1-12.5 Hz.
  - Calibration uses the inward ticks: 1-0 every 0.2 for the modulus, 0 to -120 every 40 for the phase, and 0-12 Hz
    every 2 shared by both panels. Misfit is 2.1 px in x, 2.1 px in modulus and 1.3 px in phase.
  - Runs of `zin_3wk` and `zin_4wk` use the dog 71 standard R_p, Z_c and C_PPM with L = 0.019. They reproduce both
    modulus curves at every point. With C_AR they do not (`q_fig5_standard_values`), which settles the C asked
    about in `q_figures_unread`.
  - **The phase curves are swapped relative to the legend:** the dotted line is the four-element windkessel and
    the solid line the three-element one (`q_fig5_phase_legend`). Comparisons are kept both as labelled (not
    reproduced) and swapped (reproduced).
  - The validation comparisons against the measured squares are not reproduced point by point
    (`q_fig5_vs_measured`).
  - The measured harmonics fall at 2.39, 4.78, 7.15, 9.53 and 11.91 Hz, multiples of 2.38 Hz. This supports
    `q_hr_unit`: the Table 1 heart rate is in beats/s (`q_fig5_harmonics_hr`).

Scratch renders and overlays are in `figwork/` (not committed).
