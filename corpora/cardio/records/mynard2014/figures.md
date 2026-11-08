# Figures of mynard2014

The figures are on PDF pp. 33-42 (small, with captions) and again, full page and larger, on
pp. 43-52 (no text). Readings use the full-page images (pp. 45-52), rendered at 900 dpi; the data
cite the caption pages (pp. 35-42). All figures are raster images (blurred black ink, some light grey
lines), so a 900-dpi crop is an upsampled raster.

Every reading is `mode: code`, one small file per reading in `figures/` that calls the shared code
`figures/_wave.py` with its own settings (tick labels, the curve's style, boxes masking labels). The
docstring of `_wave.py` says how the axes are calibrated (tick marks found on the image, matched in
order to the printed labels, straight-line fit; the largest tick misfit is added to every interval), how
solid, dashed and grey lines are told apart, and how the 95% intervals are set (line centre ± 2 px on a
clean run; the whole covering run where a dashed or grey line lies under black ink; on time axes
without ticks, the uncertainty of the panel's ends times the local slope). Positions the code
cannot read (a curve under another one over a steep stretch, a line clipped by the plot box, a grey line
hidden where three curves coincide) are left out of each reading's `at`. Every reading was checked with
`boxgraph figure check` and its overlay looked at (`figwork/`, not committed): the marks sit on the
intended curve.

No figure value can be compared with a model run: every curve is produced by `multiscale_coronary`,
which is not runnable here (`q_multiscale_not_runnable`), or is a measurement. What the readings allow is
recorded as comparisons between two printed curves (below) and as data for later papers' models.

## Read

- **Fig. 1** (p. 43): drawing of the 1D network, no values. Left out.
- **Fig. 2** (p. 44): circuit drawing of the 0D microvascular model, no values. Left out.
- **Fig. 3** (p. 45), model-input procedure for one animal, ten readings, x = time in s. The time axes have
  unlabelled ticks; the scale label "0.2 s" under the first interval of the LVE panel is read as a tick
  spacing of 0.2 s, with 0 on the y axis line (fitting the y axis line and three ticks to 0, 0.2, 0.4,
  0.6 s gives a misfit of 1.4-1.7 px, so the ticks are evenly spaced from the axis). The scale reading is a
  choice (`q_fig_time_axes`).
  - `fig3_aoq` AoQ (L/min, measured), y ticks 15, 10, 5 (the 0 tick is hidden by the curve; matched with
    one label dropped), misfit 1.0 px.
  - `fig3_aop` AoP and `fig3_lmp` LMP (mmHg; AoP measured, LMP the model input derived from it), ticks
    100, 95, 90, 85.
  - `fig3_lvv` LVV (mL, derived from AoQ with EF = 0.68), ticks 50, 40, 30, 20.
  - `fig3_lvp` LVP (mmHg, measured), ticks 100, 50, 0, misfit 0.7 px.
  - `fig3_cep_endo` (solid), `fig3_cep_mid` (dashed), `fig3_cep_epi` (dash-dot) CEP per layer (mmHg,
    derived). The 0 tick is hidden; the two ticks found are matched to 100 and 50 (two marks, no misfit
    check). Midwall and subepicardial lines are read only over systole (0.10-0.30 s), each with ink kept
    in its own value band (35-65 and 5-30 mmHg), where they stand apart; elsewhere they coincide with
    each other and with the solid line.
  - `fig3_lve` LVE (mmHg/mL, derived), ticks 4 and 2 matched (0 hidden), two marks.
  - `fig3_sip` SIP (mmHg, derived), ticks 20, 15, 10, 5, 0.
- **Fig. 4** (p. 46): left out. It is an illustrative waveform defining the phases S1-D2 and the
  feature points S1a-D1f; neither the caption nor the text (p. 11) says whether it is measured or
  simulated or from which animal, so a reading could not be given an origin. Its feature values are
  in Table 2 as group means.
- **Fig. 5** (p. 47), simulated (representative model, not stated which), x = time in s calibrated on the
  ticks 0, 0.2, 0.4, 0.6 (0 on the y axis line), misfit about 1 px.
  - 5A `fig5a_art` (solid, total arterial) and `fig5a_ven` (dashed, total venous) microvascular flow,
    mL/s; y ticks 3, 2, 1, 0. The labels "venous", "arterial" and the systole/diastole marker are masked.
  - 5B (arterial side) and 5C (venous side): `fig5b_en`/`fig5c_en` (solid black, En),
    `fig5b_mw`/`fig5c_mw` (solid grey, MW), `fig5b_ep`/`fig5c_ep` (dashed, Ep), mL/s. In 5C the 0 tick is
    hidden and matched with one label dropped. MW is not read where it runs under the black lines on the
    steep rises and falls.
  - 5D arterial compartment volume per layer, mL: `fig5d_en`, `fig5d_mw`, `fig5d_ep`, ticks 1.35-1.15,
    misfit 1.4 px. These are the curves the text's 17% (subendocardium) and 1.6% (subepicardium) arterial
    volume variations refer to (`volvar_endo_art_p12`, `volvar_epi_art_p12`); see `q_volvar_definition`.
- **Fig. 6** (p. 48), simulated mean normalised flow in six territories, representative adult (upper row)
  and newborn (lower row): 12 readings `fig6_<adult|newborn>_<cx|lad|septal|diag|marg|lpd>`. Each row is
  one box with vertical separators and a shared y axis (ticks 4..-1, the 4 tick hidden by the box line,
  and 2, 1, 0); each panel is read between its two separators, x as the fraction of the panel (no ticks).
  The dotted zero line is not part of the curve (only long ink components are). Misfit 1.5 px.
- **Fig. 7** (p. 49) and **Fig. 8** (p. 50), proximal Cx flow (mL/min) in nine adult sheep and nine
  newborn lambs, one panel per animal: measured (solid, `fig7a_meas` ... `fig8i_meas`, origin measured) and
  simulated (dashed, `fig7a_sim` ... `fig8i_sim`, predicted), 36 readings, at x = 0.01, 0.03, ..., 0.99 of
  the plotted interval (no x ticks: `q_fig_time_axes`). y ticks 150..-50 (Fig. 7) and 40..-20 (Fig. 8),
  misfit at most 1.8 px; where a curve touches the axis at a tick, that tick is dropped. The solid line is
  thicker than the dashes and is separated by an opening with a 21-px disk; the dashed curve is read
  dash by dash, interpolated across the 21-px gaps of its dash pattern, and where it runs into the solid
  line it is given the whole black run there. Positions on steep stretches where both lines overlap, and
  the bottom of the Fig. 7D and Fig. 8B measured lines where they touch the plot box, are left out. The
  arrows of Fig. 7B are masked. Each panel's simulated curve is compared with its measured one
  (`cmp_fig7a` ... `cmp_fig8i`, purpose validation): this is the paper's own visual validation, now
  pointwise with intervals (both curves of a panel are read at the positions readable on both). All 18
  come out not reproduced, as the paper's own RMS errors (about 15% of maximal flow) and its list of
  underestimated features lead one to expect (`q_fig78_pointwise`).
- **Fig. 9** (p. 51), sensitivity of the simulated Cx flow (mL/min), six panels, x as the fraction of the
  plotted interval: baseline solid line in every panel (`fig9a_base` ... `fig9f_base`), the dashed and grey
  perturbations (A: 7 m/s dashed, 11 m/s grey; B: no shift, dashed; C: no SIP grey, double SIP dashed;
  D: half C1 dashed, double C1 grey; E: half Cpa dashed, double Cpa grey; F: double V0 grey, half V0
  dashed): 17 readings. Labels and leader lines are masked. The grey lines are not read where they lie
  under the black lines and the three curves coincide (start of the beat, the upstroke, and in C after
  the upstroke). The baseline of panels B-F is compared with that of A (`cmp_fig9b_base` ...
  `cmp_fig9f_base`, consistency): the caption implies one unperturbed simulation in all panels. C, E and
  F come out close; B and D each miss at one position, within about 1-2 mL/min elsewhere
  (`q_fig9_baselines`).
- **Fig. 10** (p. 52), simulated.
  - 10A pressure-area relation at the conduit artery (mmHg against mm², ticks 75, 70, 65 and 11.1, 11.2,
    11.3; 60 at the corner has no tick): `fig10a_elastic` (solid, 11.13-11.32 mm²), and the
    viscoelastic loop's two branches, `fig10a_visco_upper` (dash ink above the solid line, 11.19-11.32)
    and `fig10a_visco_lower` (below it, 11.19-11.27). The small inner loop near 11.14-11.18 mm², where the
    branches cross the solid line, is not read.
  - 10B Cx flow (mL/min) against time, ticks 0, 0.2, 0.4 s (0 on the axis), misfit 0.2 px:
    `fig10b_elastic` (solid) and `fig10b_visco` (dashed).

## Bearing on open questions

- `q_figures_not_read`, `q_measured_waveforms_unread`: the measured waveforms of Figs. 7-8 and the
  simulated curves of Figs. 3, 5, 6, 9 and 10 are now read (`q_figures_read`).
- Fig. 5D bears on the arterial volume variations printed on pp. 12 and 16 (17%, 1.6%), but the paper
  does not say relative to what the variation is taken, so no comparison is recorded
  (`q_volvar_definition`).
