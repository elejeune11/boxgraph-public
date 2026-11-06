# Figures of shi2013_ch2

Every figure that plots values is a low-resolution raster (one raster pixel is about 6 px at 900 dpi),
black on white, drawn by the same plotting program as the authors' korakianitis2006 figures. All
readings use one method (`figures/_shi.py`, adapted from korakianitis2006's `_kor.py`): each panel is
rendered at 900 dpi; the axes are the strongest ink column and row; inward tick marks are matched in
order to the printed labels and a straight line is fitted to them (its misfit, in px, widens every
interval); hollow markers (squares, diamonds, triangles) are filled so a marker is read at its centre;
at each x the ink within +-9 px is split into separate tracks and the reading takes the track it names
(counted from the top or the bottom, with the number of tracks it expects there). Where two curves
coincide they form one track and the reading is of both. Near-vertical stretches (a track over 90 px
tall) are not read. The legend region is masked. Only positions the code reads are listed in `at`.
Every reading was checked with `boxgraph figure check`: the marks sit on the intended curve or markers.

The waveform readings are compared with `circulation_ch2_waveform`, the record's circulation model
(circulation_ch2 as printed, with the record's added initial values) evaluated at the figure's times
in the configuration the figure shows; for valve dynamics and all features also with the corrected
Eq. 2-13 (`signed: true`, as circulation_ch2_signed). Elastance readings are compared with
`elastance_ch2` (Eqs. 2-2, 2-3, 2-5, 2-6). In the comparison figures (2-10, 2-11, 2-14, 2-17, 2-20)
the unprimed curves repeat the simplified model of Fig. 2-9; only the primed curves (the configuration
of the figure) are read, where they can be told apart. Calibration misfits: 0.5 px on every x axis
(2.0 px on Fig. 2-3); 0.5 to 4.8 px on the y axes.

## Read

- **Fig. 2-3** (p. 7), measured LV volume over 33 MRI phases: `fig2_3_vlv_mri`, the square markers at
  phases 1-32 (bottom track; phase 33 sits on the axis frame and is not read). y misfit 3.0 px.
  Origin `measured`; no error bars are drawn. No model in the record predicts volume per MRI phase
  (the phase-to-time mapping is not stated), so it has no comparison; it is kept for validation by a
  model that does.
- **Fig. 2-6** (p. 12), elastances: `fig2_6_elv` (solid E(lv)), `fig2_6_ela` (dotted E(la), with its
  atrial-contraction bump). y misfit 0.5 px. Compared with `elastance_ch2`.
- **Fig. 2-9(a)-(f)** (pp. 24-26), simplified model: `fig2_9a_psas`, `fig2_9a_pla`, `fig2_9b_qao`
  (decay after the peak), `fig2_9b_qmi` (decay after the E peak), `fig2_9c_vlv`, `fig2_9c_vla`,
  `fig2_9d_ppas`, `fig2_9d_pra`, `fig2_9e_qpo` (decay after the peak), `fig2_9e_qti` (diastasis),
  `fig2_9f_vrv`, `fig2_9f_vra`. y misfits 1.5-2.6 px. P(lv) and P(rv) are read only where they
  coincide with P(sas), P(pas) (elsewhere they are near-vertical or merge with the atrial curves);
  P(sat), P(svn), Q(sas), Q(sat), Q(svn) and their pulmonary twins coincide with or sit close to other
  curves over most of the cycle and are not read. Compared with the simplified configuration.
- **Fig. 2-10** (pp. 28-29), atrial contraction alone: `fig2_10a_psas`, `fig2_10b_qao`,
  `fig2_10b_qmi` (late E decay, where primed and unprimed coincide), `fig2_10c_vlv` (end-diastolic
  plateau below the FV1 ellipse, and filling), `fig2_10c_vla` (the atrial-contraction trough),
  `fig2_10d_ppas`. P(la)', P(lv)' in diastole and the right-atrial curves of (d) lie within 1-2 mmHg of
  the unprimed curves and the FP1 ellipses: not separable.
- **Fig. 2-11** (pp. 30-31), KG diaphragm alone: `fig2_11a_psas`, `fig2_11c_vlv`, `fig2_11c_vla`,
  `fig2_11d_ppas` (four positions only). Panel (b): primed and unprimed flows coincide except at the
  near-vertical peaks; not read.
- **Fig. 2-12** (p. 31), KG displacement L(mm): `fig2_12_l`, the only curve, 59 positions (the steep
  descent and return are partly not read). y misfit 2.2 px. This is the direct check of Eqs. 2-10 to
  2-12 that q_kg_units asks for: compared with the KG + atrial run.
- **Fig. 2-13** (p. 31), elastances again: `fig2_13_elv`, `fig2_13_ela`, as Fig. 2-6.
- **Fig. 2-14** (pp. 32-33), KG diaphragm with atrial contraction: `fig2_14a_psas` (primed and
  unprimed coincide), `fig2_14c_vlv`, `fig2_14c_vla` (trough), `fig2_14f_vrv`, `fig2_14f_vra`. Panels
  (b), (d), (e): the primed curves coincide with the unprimed except at the A wave and FP1, which lie
  inside annotation ellipses; not read.
- **Fig. 2-15** (p. 37), leaflet angles, simplified model (x axis 11-12.2 s): `fig2_15a_ao`,
  `fig2_15a_mi`, `fig2_15b_po`, `fig2_15b_ti`, each at 75 degrees while open and 0 while shut,
  every 0.04 s away from the jumps. Compared with the on-off valve state of the model (theta_max while
  the valve passes forward flow).
- **Fig. 2-16** (pp. 37-38), leaflet angles with valve dynamics: `fig2_16a_ao`, `fig2_16a_mi`,
  `fig2_16b_po`, `fig2_16b_ti`; the transitions are near-vertical and not read.
- **Fig. 2-17** (pp. 38-40), valve dynamics alone: `fig2_17a_psas`, `fig2_17c_vlv`, `fig2_17c_vla`,
  `fig2_17d_ppas`, `fig2_17d_pra` (P(ra)', with P(rv)' while the tricuspid valve is open),
  `fig2_17f_vrv`, `fig2_17f_vra`. Panels (b), (e): the primed and unprimed flows differ mainly in the
  regurgitant spikes (FQ1), near-vertical and inside annotation ellipses; not read (see
  q_fig_regurgitant_flow).
- **Fig. 2-18** (p. 42), KG displacement, all features (solid) and KG + atrial (dotted):
  `fig2_18_l_all` (bottom track; it coincides with the dotted line outside the systolic trough) and
  `fig2_18_l_kgat` (the dotted line where it separates, two positions).
- **Fig. 2-20** (pp. 44-45), all features: `fig2_20a_psas`, `fig2_20c_vlv`, `fig2_20c_vla`,
  `fig2_20d_ppas`, `fig2_20d_pra`, `fig2_20f_vrv`, `fig2_20f_vra`. Panels (b), (e): as Fig. 2-17(b),
  (e); not read.
- **Fig. 2-21** (p. 46), zoom of Fig. 2-20(a) at end diastole: `fig2_21_pla`, P(la) and P(la)'
  together after mitral closure (10.04-10.1 s). Before that the four curves cross within 1-2 mmHg
  inside the FP1 ellipse, and the ventricular upstroke is near-vertical: not read.

## Left out

- Figs. 2-1, 2-2 (p. 7): an MRI slice and a reconstructed geometry, no values.
- Fig. 2-4 (p. 9): conceptual textbook drawings without values.
- Figs. 2-5, 2-7, 2-8 (pp. 11, 15, 17): schematics.
- Fig. 2-19 (p. 43): the four angle curves (valve dynamics alone and all features) coincide on every
  plateau and differ only in the near-vertical transitions; the plateaus are already read in Fig. 2-16.
- The flow panels named above (2-11(b), 2-14(b), (e), 2-17(b), (e), 2-20(b), (e)) and the curves named
  under each figure, for the reasons given there.

## What the figures settle

- **Eq. 2-13's sign (q_eq2_13_sign).** Figs. 2-17(b), (e) and 2-20(b), (e) plot negative valve flows
  (FQ1, down to about -300 to -400 ml/s on the axes), which Eq. 2-13 as printed cannot produce: the
  plotted curves were computed with the minus sign on the reverse branch. New question
  q_fig_regurgitant_flow.
- **KG displacement (q_kg_units).** Fig. 2-12 is now a calibrated curve (peak about -27.5 mm at
  10.30 s, +3.3 mm plateau in diastasis, +6.2 mm at the atrial bump), compared point by point with
  the KG + atrial run of Eq. 2-10 as printed.
- **E_lv,d.** Figs. 2-6 and 2-13 read E(lv) in diastole at about 0.068 mmHg/ml, against E_lv,d = 0.1 in
  Table 2-1, while E(la) reads 0.148, consistent with E_la,min = 0.15. New question q_fig_elvd.
- **theta_max (q_theta_max).** Figs. 2-15 and 2-16 read the open angle at 74.9-75.3 degrees on every
  valve: the 75 degrees of theta_max_added.
- **Initial values (q_initial_values).** The readings of Fig. 2-9 give whole waveforms (aortic
  pressure 85-117 mmHg, pulmonary 13-25.5 mmHg, LV volume 51-121 ml) against which the added initial
  values and their alternatives can be judged.
