# Figures of yong2025

Figure pass of 2026-11-09. Every plotted result is read with code (`mode: code`). The reading code for each
curve is a few lines in `figures/<reading id>.py`; the method is shared in `figures/_wave.py`:

- **Calibration.** The axis lines are found as the longest dark runs in the crop and the tick marks as short dark
  runs just outside them. The ticks are matched in order to the printed tick labels (an unlabelled tick between
  labelled ones is skipped, not given a value), and a line is fitted through them. The worst tick residual (at
  least 0.5 px) widens every interval. Unless noted below, the misfit is 0.5-1.7 px.
- **Curves.** Each curve is found by its colour inside the plot area. Black lines are opened with a horizontal
  element, which removes the thin dashed and solid phase markers. Dashed and solid lines of one colour are told
  apart by the width of their pieces. The curve is traced column by column. At each x the value is the centre of
  the line, and the interval spans the line's thickness, the calibration misfit and the change across the x
  misfit. Between dashes, or where another curve hides the line, the nearest traced columns on either side are
  joined. Where named curves are drawn over it (`under`), the line is read as their joint line. Where it runs
  along the x axis (`on_axis`), it is read as the axis line's extent. Each case is said in the reading's note.
- **Resolution.** All figures are raster images embedded in the PDF at a lower resolution than the 1200 dpi
  render. Rendering finer adds no information, so line thickness, not pixel size, sets most intervals.
- **x positions.** Waveforms are read at 0.025, 0.075, ..., 0.975 of the cycle (Fig. 3A: of the first of its
  two plotted cycles; Fig. 6C: 0.075-0.775, where the in vivo curve is drawn). Bars are read one by one, with x the
  bar's position.

Model side: `coronary_waveform` samples the rebuilt closed loop (coronary_closed_loop, unchanged) at those x
positions. Phase 0 is the onset of ventricular contraction (q_fig_phase_origin), and there is one run per
configuration (wf_*). `rmicro_waveform` (Eqs. 10-11) and `elastance_waveform` (Eqs. 3-4) give Rmicro(t) and
E(t). `bars_*` arrange the five configurations' scalar results by bar position for Fig. 7C-D.

## Per panel

- **Fig. 1**: circuit drawing, no values. Left out.
- **Fig. 2A**: the reference resistance waveform of Sen et al. 2013 (measured) with the linear and squared
  equations. Left out: the y axis has no tick labels, so the curve cannot be calibrated. The x axis is labelled only
  0.0 and 4.0 s. Its caption's numbers are recorded as data.
- **Fig. 2B**: `fig2b_rmicro_lad`, the black Rmicro(t) curve (LAD, normal). x ticks every 0.1 s (labelled 0.0,
  0.5, 1.0), y 0/50/100/150, misfit 0.5/0.8 px. The red constant Rbar line is a different colour and is not
  read. Compared with rmicro_waveform (rw_lad). The read minimum (42.8) and maximum (124.2) agree with the
  caption's 42.92 and 124.84.
- **Fig. 2C**: `fig2c_rmicro_rca`, as for 2B (RCA). Compared with rw_rca.
- **Fig. 3A** (four inset panels, two cycles each; read over the first cycle, x ticks 0/1/2):
  - aortic pressure: `fig3a_aop_normal` (black) and `fig3a_aop_ph` (red dash-dot). The two lines coincide; black is
    read where it shows and otherwise under the red.
  - aortic flow: `fig3a_aoq_normal`, `fig3a_aoq_ph`. In diastole both lie on the x axis (read as the axis line, 0 ±
    its thickness).
  - pulmonary artery pressure: `fig3a_pap_normal`, `fig3a_pap_ph`.
  - pulmonary artery flow: `fig3a_paq_normal`, `fig3a_paq_ph`.

  All are compared with wf_vrimp / wf_vrimp_PH (p_ao, q_ao, p_pa, q_pa). The caption does not say which model Fig.
  3 shows. Its resistance panel varies in time, so the new model is assumed.
- **Fig. 3B**:
  - PV loops: left out. They are closed loops (volume against pressure, two values per volume) with a shaded area.
    The rebuild does not output chamber volume waveforms.
  - Elastance: `fig3b_elast_lv_normal`, `fig3b_elast_rv_normal`, `fig3b_elast_lv_ph` and `fig3b_elast_rv_ph`
    (blue LV, red RV). The flat diastolic parts overlap and are read under the other line. Compared with
    elastance_waveform on Supp. Table S1's values (RV E_max 1.00 in PH).
  - Normal resistance: left out. It is the same pair of curves as Figs. 2B-C (which are read), and its red RCA curve
    crosses the red and blue Rbar lines and their labels.
  - PH resistance: `fig3b_rmicro_rca_ph`, the saturated red RCA curve. The paler red mean line (231.29) is removed as
    a long horizontal run. In diastole the curve is read under the purple overlap with the blue LAD lines. The PH
    LAD curve equals the normal one and is not read again. Compared with rw_rca_PH. **This settles q_kph_form**
    (question q_fig3b_kph): the curve peaks near 890 mmHg.s/ml, as Eq. 11 with k_PH outside the square root gives
    (902).
- **Fig. 4A-C** (per model): left out as a duplicate. They are the same nine curves as Figs. 4D-F, regrouped by
  model, and Figs. 4D-F are read.
- **Fig. 4D-F** (per vessel): nine readings `fig4{d,e,f}_{lad,lcx,rca}_{vrimp,rimp,vr}` (red VR + IMP, blue Rbar +
  IMP, green VR). y ticks every 0.5 (labelled 0, 1, 2), misfit 0.5 px. Compared with wf_vrimp / wf_rimp / wf_vr
  (q_lad, q_lcx, q_rca).
- **Fig. 5A-C**: `fig5a_gcv_vrimp`, `fig5b_gcv_rimp`, `fig5c_gcv_vr`. In 5A-B the x axis is drawn at y = 0 inside
  the plot, and the curve is followed below it. In 5A-B the tick labelled 6 sits about 10 % further from 4 than 4
  from 2 (y misfit about 13 px, carried in the intervals; question q_fig5_peak, the plotted peak about 6.0 against
  Table 1's 5.39). Compared with wf_* (q_gcv).
- **Fig. 6A-C**: the in vivo curves (purple dashed, 'Validation'), each read twice:
  - on the right axis, as measured: `fig6a_lad_invivo` and `fig6b_rca_invivo` (Doppler flow velocity, cm/s,
    Seligman et al. 2022) and `fig6c_gcv_invivo` (MR flow, ml/s, corrected for a CSA of 17 mm², Bedaux et al.
    2001). Origin `measured`.
  - on the left 'Simulated flow' axis (`*_invivo_scaled`), which is the measurement as the paper rescaled it to
    the models' stroke volume. Origin `derived`.

  The scaled curves are validated against the rebuild in all three configurations. The simulated curves of Fig. 6
  are left out: they are Figs. 4D, 4F and 5's curves redrawn on a time axis shifted to the in vivo cycle, in a way
  the paper does not state (q_fig_time_alignment). The MAE values of Eq. 15 are still not recomputed, because that
  needs the paper's alignment.
- **Fig. 7A-B**: `fig7{a,b}_lad_*` (black: LAD, normal and PH, 'unchanged'), `fig7{a,b}_rca_*` (red solid,
  normal) and `fig7{a,b}_rca_*_ph` (red dashed, PH). The solid and dashed red lines are separated by the width of
  their pieces (120 px). The black LAD is compared with both the normal and the PH runs.
- **Fig. 7C**: stacked bars, read bar by bar (`fig7c_{lad,rca}_mean` for the whole bar, `fig7c_{lad,rca}_sys`
  for the darker 'Sys' segment). The dotted fill is handled by taking each row's median colour across the bar.
  Compared with the rebuild through bars_mean_flow and bars_sys_part (Qs_mean x systolic fraction). The bar tops
  read 0.02-0.04 ml/s above the printed labels for the VR + IMP bars (q_fig7c_bars).
- **Fig. 7D**: `fig7d_{lad,rca}_mdsfr`. Bars agree with their printed labels (4.1, 4.1, 2.4, 2.4; 2.2, 6.3, 1.3,
  1.7) to 0.01. Compared with the rebuild's mDSFR by Eq. 14 as printed and as a ratio of means.
- **Fig. 8A-B**: the in vivo PH curves (van Wolferen et al. 2008), read on the right axis (MR flow, measured:
  `fig8{a,b}_*_invivo`) and on the left axis (rescaled: `*_invivo_scaled`, validated against wf_vrimp_PH and
  wf_rimp_PH). The simulated curves are left out for the same reason as in Fig. 6: they are Fig. 7's PH curves on a
  shifted time axis.
- **Supp. Fig. S1A-C**: `figs1{a,b,c}_pao_*`, the black central aortic pressure Pa. It is read where it shows and
  otherwise under the Pd lines. The three Pd lines (LAD green, LCx blue, RCA dark red) are left out: they lie on top
  of one another over almost the whole cycle (curves indistinguishable). Compared with wf_* (p_ao).
- **Supp. Fig. S2A-C**: `figs2{a,b,c}_lcxvein_*` (LCx venous flow). Compared with wf_* (q_lcx_vein).

## What the comparisons show

- **Reproduced point by point** (closed form):
  - Figs. 2B-C (Rmicro(t), 20/20 points each);
  - Fig. 3B elastances (all four curves);
  - Fig. 3B PH RCA resistance. This settles q_kph_form: k_PH multiplies the square root.
- **Not reproduced** (closed-loop waveforms: Figs. 3A, 4, 5, 7, S1-S2):
  - The rebuild's absolute levels are low. Its aortic pressure is 41-70 against the plotted 56-131 mmHg, and its
    coronary flows are about 0.7 times the plotted ones. This matches the record's scalar comparisons: the added
    circulating volume (P_init, q_volume) scales every absolute value. Only Fig. 3A's normal PA pressure comes
    close (16/20 points).
  - The shapes keep the paper's ordering between models.
  - The 7C-D bars inherit the same scaling. The mDSFR bars are missed under both readings of Eq. 14.
- **Validation against the rescaled in vivo curves** (at the same phase, not the paper's alignment):
  - agree: Fig. 6B RCA with VR + IMP and VR (20/20); Fig. 6C GCV with both IMP models (15/15).
  - close: Fig. 6A LAD with Rbar + IMP.
  - not reproduced: the rest. In PH (Fig. 8), points agree in diastole but not in systole.

  The paper's MAE values remain unchecked (q_fig_time_alignment).
