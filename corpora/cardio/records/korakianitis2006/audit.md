# Audit of korakianitis2006

A second, independent reading of `corpus/cardio/2006_Korakianitis.pdf` against the record, checked
on the page images (pp. 4-9, 11, 13, 15, 17). Figures were not read.

## Transcription checks (no changes needed)

- Tables 1-5 (pp. 7-8): all parameter data (CQ, E, P0, V0, C, R, L, K_p/K_f/K_b/K_v, angles,
  DT, T, Ts, T_pwb, T_pww) match the page images in digits, units and page. No exponents are involved.
  Kb/Kv units (printed rad/(s m)) and Kp_mi (printed m/(s2 mmHg)) are entered with a corrected unit and
  a note. This is a unit judgement, and it is already recorded in q_table3_units.
- Results data, pp. 8, 9, 11, 13, 15, 17: plv/psas ranges (0-130, 90-130), co 5, vlv 50/120, sv 70,
  126.4/117.9, 26.8/26.1, 702.9/826.0, 631.7/861.0, 983.4/1128.3, 712.1/844.1, 134.3, 77.3, 298.7,
  306.9, 24%, 117.8/110.4, 161.6, 80.9, 132.7, 86.5/69.3, 17, 1128.3/1270.2, 123.4/149.0 all match
  the page images.
- Every printed decimal result on pp. 10-17 was searched for in the text, and each one is in
  data.yaml. The ones left out (timings, ranges written in words, 47.9 ml/s) are explained in
  source.yaml notes.

## Model checks (no changes needed)

- circulation_valves, Eqs. 1-5 (p. 4-5): Eq. 2, Eq. 3 (both cos branches, including
  (t + T_s2 - T_s1)/T_s1), Eq. 4 and Eq. 5 match the printed equations.
- circulation_valves, Eqs. 6-8 (p. 5): Eq. 6 (both branches +sqrt, as printed), Eq. 7 and Eq. 8
  match.
- circulation_valves, Eq. 14 (p. 6): the K_p, K_f and K_b terms are on both branches, and the
  -K_v Q sin(theta) term only for Q >= 0, as printed. vortex_angle_factor 2 reproduces Eq. 13's
  sin(2 theta).
- circulation_valves, Eqs. 15-20 (p. 6): Eq. 18 uses P_sas - P_svn as printed, and the pulmonary
  loop mirrors it.
- valve_area_eq8 (p. 5), stroke_volume (p. 9) and pressure_drop (p. 15) match the equation or the
  arithmetic they encode.

## Added inputs

- added.yaml: Ts1, Ts2 and the initial atrial volumes and vessel pressures each have a basis and real
  alternatives. The zero initial vessel flows and the starting leaflet angle (theta_min) are not in
  added.yaml, but the starting angle is covered by q_angle_limits. Initial flows do not change the
  circulating volume, so no change was made.

## New open questions (questions.yaml)

- q_audit_about_values (p. 8, 9, 15): disagreement with the first reader. co_simplified,
  vlv_max/min_simplified, qmi_max/min_stenosis, qmi_A_stenosis and psas_ed_drop_regurgitation are
  printed with "about"/"approximately" but entered without "~", so they get verdicts. Kept as
  entered, since this is the first reader's judgement.
- q_audit_fig_angles (p. 13, Fig. 10; p. 15, Fig. 12): seen by eye, the healthy leaflets close at
  about 0 deg (not Table 4's 5 deg), and the stenotic mitral leaflet sits near 45 deg rather than
  50 deg. This supports q_theta_min_ao, and the figure job should read these angles.
- q_audit_fig5_volume (p. 9, Fig. 5): seen by eye, the LV volume is about 55-130 ml and the peak LV
  pressure about 133 mmHg, against the printed "50 and 120 ml" and 130/126.4 mmHg. For the figure
  job.

## Not changed, noted

- qti_systole_simplified / qti_systole_normal (p. 13) are still not compared (two validator
  warnings). This is the first reader's scope decision, already recorded in q_tricuspid_systole, and
  I agree with it.
- source.yaml `reader.model` is `None`. This is metadata, left as is.

## Revisit: corrected variants

Read under the guide's rule "An evident misprint gets a corrected variant beside the printed
model". The printed models (circulation_valves, circulation_waveform, elastance_eq2_5), their runs and
comparisons, and every possible_error question are unchanged. Every CellML line cited below was read
in `corpus/cardio/code/shi_cellml_systemic/` (the record shi_cellml_systemic, not edited).

### Corrections made (each in models/circulation_valves_corrected, _corrected_sin, circulation_waveform_corrected, _corrected_sin; Eq. 3 also in elastance_eq2_5_corrected)

- **Eq. 3, ventricular activation (q_eq3_activation, q_fig2_eq3; p. 4).** Printed: cos(pi t/T_s1), then
  cos(pi (t + T_s2 - T_s1)/T_s1), then 0 (checked again on the page image). Corrected to 1 - cos(pi t/T_s1),
  then 1 + cos(pi (t - T_s1)/(T_s2 - T_s1)), then 0. Evidence: (i) with Eq. 2 and Table 1 the printed form
  gives a negative elastance (-1.1 mmHg/ml at T_s1) and jumps at 0, T_s1 and T_s2; (ii) Fig. 2 (p. 4,
  reading fig2_elv) shows E(lv) rising smoothly from its diastolic level to 2.5 mmHg/ml at about 0.3 s and
  back by 0.45 s; (iii) EVentricle.cellml line 20 has exactly the corrected form (with E = Emin + et
  (Emax - Emin)/2, the printed Eq. 2). Evident: the figure, a sign argument and the authors' code agree.
- **Eq. 6, sign of the reverse branch (q_eq6_sign; p. 5).** Printed: +CQ AR sqrt(P_sas - P_lv) for
  P_lv < P_sas. Corrected to -CQ AR sqrt(P_sas - P_lv), for all four valves. Evidence: as printed no valve
  flow can be negative (flow against the pressure difference), yet the paper reports reverse-flow
  amplitudes 134.3, 77.3, 298.7 and 306.9 ml/s (p. 13); TempCDv.cellml line 48 has the factor -1 on that
  branch. It matters only with leaflet dynamics (Eq. 7 sets AR = 0 on that branch).
- **Eq. 18, driving pressure of the artery flow (q_eq18_psas; p. 6).** Printed: P_sas - P_svn. Corrected
  to P_sat - P_svn, and P_pat - P_pvn in the pulmonary loop ("similar to that of the systemic loop", p. 6).
  Evidence: the text says the artery is "similar" to the aortic sinus (Eq. 16 uses the segment's own
  pressure); Fig. 1 (p. 4) draws C_sat at the node P_sat and Q_sat leaving it through R_sat and L_sat; as
  printed C_sat is charged by Q_sas but drives nothing; TempRLC.cellml line 25 applied to Sat
  (ModelSys.cellml lines 69-79) with the series resistances of TempR.cellml line 19 gives exactly
  (P_sat - P_svn - (R_sat + R_sar + R_scp) Q_sat)/L_sat. (This pass added Fig. 1 to the evidence text and
  corrected the line range 70-78 to 69-79 in the four model.yaml files.)
- **Eq. 14, vortex term (q_eq13_eq14; p. 6): two readings, two variants.** Eq. 13 prints k_v Q sin 2theta
  and the text says the vortex is strongest at about 45 deg and weaker below and above, which sin 2theta
  does and sin theta (maximum at 90 deg) does not; Eq. 14 prints sin theta. No released code has valve
  dynamics, so either could be the one the authors ran: circulation_valves_corrected (and
  circulation_waveform_corrected) use sin 2theta; circulation_valves_corrected_sin (and
  circulation_waveform_corrected_sin) keep Eq. 14 as printed. Runs with on-off valves or K_v = 0 (Figs. 5,
  6; Section 3.1) do not depend on it and are run once.

### Corrections not made

- **q_table3_units (p. 7).** A unit question about printed numbers (K_b, K_v in rad/(s m), K_p,mi in
  m/(s2 mmHg)), not an equation. The record already enters these values in the only dimensionally
  possible units, with the question; nothing to correct in a model.
- **q_theta_min_ao, q_fig_closed_angle (pp. 8, 15; Figs. 6, 7, 10, 12).** Table 4's theta_min = 5 deg
  against the text's "from 0 to 25" and the figures' closed angles near 0 deg. These are printed numbers;
  the guide forbids correcting a number through a variant, so every variant run keeps Table 4 (the first
  reader's choice). The closed-angle figure comparisons of the variants therefore still differ by about
  5 deg on that account, as the printed model's do.

### Initial conditions

- Vlv_init_cellml (added.yaml): 500 ml, the LV initial volume of ParaLeftHeart.cellml line 27, as an
  alternative to the record's Vlv_init_table2 (800 ml, kept for every run). The code's other initial
  values (LA 20 ml, line 28; P_sas, P_sat 100 mmHg, ParaSys.cellml lines 17, 23; P_svn 0, line 32) are
  already the record's added values. The code has no right heart or pulmonary loop, so it states no
  right-side initial value. The scalar runs of both variants are repeated with it (run ids ending `_ic`).

### Runs and comparisons added

- Runs `run_*_corr` (sin 2theta), `run_*_corr_sin` (sin theta) and `run_*_corr_ic`, `run_*_corr_sin_ic`
  repeat run_simplified, run_normal, run_stenosis and run_regurgitation with the same inputs, and are
  compared (`cmp_*_corr...`) with the same printed results. Every figure run has a `_corr` twin and,
  where the vortex term acts (Figs. 7-13), a `_corr_sin` twin, compared with the same figure readings.
  Fig. 2 is compared through elastance_eq2_5_corrected.
- Fix (this pass): run_fig2_elv_corr and run_fig2_ela_corr fed the whole circulation input set
  (`*base`) to elastance_eq2_5_corrected, whose ports are only the nine elastance and timing inputs;
  the build refuses unknown inputs. They now take the same inputs as run_fig2_elv / run_fig2_ela.

### What the variants reproduce

Verdicts read from a build of this record against the shared run cache (`build/cache`), with no new
simulation. Counts are comparisons. "IC 500" means the runs ending `_ic` (LV initial volume 500 ml from
the CellML code). Every other variant run uses the record's initial conditions (Table 2, 800 ml).

| model | reproduced | close | not reproduced |
|---|---|---|---|
| circulation_valves (printed) | 0 | 0 | 42 |
| circulation_valves_corrected (sin 2theta) | 0 | 1 | 36 |
| circulation_valves_corrected, IC 500 | 1 | 0 | 36 |
| circulation_valves_corrected_sin | 0 | 0 | 22 |
| circulation_valves_corrected_sin, IC 500 | 0 | 1 | 21 |
| circulation_waveform (printed) | 0 | 0 | 72 |
| circulation_waveform_corrected (sin 2theta) | 10 | 5 | 57 |
| circulation_waveform_corrected_sin | 8 | 3 | 43 |
| elastance_eq2_5 (printed) | 1 | 0 | 1 |
| elastance_eq2_5_corrected | 2 | 0 | 0 |

The printed circulation model reproduces nothing. It gives an LV pressure of about 4000 mmHg and
negative atrial volumes, because Eq. 3 makes the elastance negative. Once Eqs. 3, 6 and 18 are corrected
the circulation runs at physiological magnitudes, and the remaining differences are mostly offsets that
the unstated initial volume controls. The rest of this section covers each table, text result and
figure.

**Scalar results in the text (pp. 8-17).**
- With Table 2 initial conditions, the corrected variants run about 20-30% high on every pressure and
  volume. For example, peak P_lv is 155.0 against 126.4 (simplified) and 146.8 against 117.9 (normal),
  and V_lv is 66-169 ml against 50-120 ml. Only co_simplified comes out close (6.19 against 5 L/min).
- With IC 500 the same variants land on the printed left-side pressures: peak P_lv 125.4 against 126.4
  and 117.3 against 117.9, peak P_sas 125.3 against 126.4 and 117.1 against 117.9, P_sas range 86.1-125.3
  against "90-130", end-diastolic P_sas 83.2 against 86.5 and 66.3 against 69.3. The peak aortic flow
  with regurgitation is 1274.9 against 1270.2 ml/s, and the cardiac output is reproduced (4.98 against 5).
  Most of these are within 1-5%, but they are still "not reproduced" at the printed precision. With
  sin theta and IC 500, peak P_sas normal is close (118.0 against 117.9) and the aortic reverse-flow
  amplitude is 135.4 against 134.3 ml/s.
- Every variant and initial condition still misses these results:
  - right-side peaks: P_pas and P_rv are about 45 mmHg with IC 500 (57 with Table 2) against 26.1/26.8;
  - mitral E wave: +13% (normal) and +15% (simplified) with IC 500;
  - tricuspid E wave: -15% (normal) and -5% (simplified);
  - pulmonary reverse flow: 162-252 against 77.3 ml/s;
  - stenotic mitral flows: A wave 177-208 against 132.7, maximum 256-293 against 161.6;
  - V_lv: end-diastolic +7% to +11% with IC 500, and SV 83 against 70 ml.
  The code states no right-side initial volume, so the right-side offset stays an unstated input. The
  stenosis misses do not depend on initial conditions.
- The two Eq. 14 readings differ by less than 1% on pressures and volumes. sin theta is nearer on the
  reverse-flow amplitudes (aortic 135.4 against 155.0, pulmonary 162 against 226), but no scalar result
  separates them decisively.

**Figures (Table 2 initial conditions only; the figure runs have no IC 500 twin).**
- Fig. 2: the printed Eq. 3 fails E_lv (it jumps to 1.3 mmHg/ml at t = 0). The corrected Eq. 3
  reproduces both E_lv and E_la (E_la was already reproduced).
- Fig. 5 (simplified, on-off valves): Q_mi reproduced, Q_ao and Q_ti close. Pressures and volumes are
  not reproduced, with the same offsets as the scalar runs: about +6 mmHg on P_la and P_lv, +13 mmHg on
  P_ao, +7 mmHg on P_ra and P_rv, +28 mmHg on P_po, and +31 to +46 ml on volumes. Q_pa is not reproduced
  either.
- Fig. 6 (on-off leaflet angles): not reproduced. The open angles match (75 deg). The closed angle is
  Table 4's 5 deg against about 0 deg in the figure (q_theta_min_ao, q_fig_closed_angle), and the
  switching times differ.
- Fig. 7 (leaflet dynamics, normal): not reproduced. On the opening mitral angle sin 2theta is within
  0.1 deg at the first read positions, against 4-5 deg for sin theta. On the tricuspid angle sin theta is
  nearer (2.7 deg against 5.1 deg). Both keep the 5 deg closed angle.
- Fig. 8 (Eq. 14 terms): the velocity term in 8b is reproduced by both readings. The pressure term in 8b
  is reproduced by sin 2theta only, the one figure comparison that separates the two readings. The vortex
  term in 8b is close for both, and 8a is not reproduced.
- Fig. 9 (normal): Q_mi reproduced and Q_ti close (both readings). Q_ao, Q_pa, pressures and volumes are
  not reproduced, with the same offsets as Fig. 5.
- Fig. 10 (angles, normal and stenosis): not reproduced. For the normal mitral leaflet, sin 2theta again
  tracks the opening curve to within 0.2 deg, and the miss is the closed angle.
- Fig. 11 (mitral stenosis): Q_mi and Q_ti reproduced (both readings). The other eleven readings are not
  reproduced.
- Fig. 12 (aortic angle): the regurgitant valve (closed at 25 deg) is reproduced by both corrected
  readings and not by the printed model. The normal valve misses by Table 4's 5 deg.
- Fig. 13 (aortic regurgitation): Q_ao (the reverse flow, about -48 ml/s against the read -44), Q_mi and
  Q_pa are reproduced, and Q_ti is close (both readings). Pressures and volumes are not reproduced.

**Reading of these results.** The corrections of Eqs. 3, 6 and 18 are what make the model run at all.
With them, every flow waveform the paper plots for the left heart is reproduced or close, as are the
regurgitant closed angle and the Fig. 8b terms. What remains has two causes:
- Offsets in pressure and volume. They shrink to a few percent on the left side when the CellML code's
  initial volume is used, so they trace mainly to the unstated initial conditions.
- The 5 deg closed angle of Table 4 (q_theta_min_ao).

Not explained by any correction or initial condition: the right-side pressures (about 45 against 26
mmHg), the pulmonary reverse flow, and the stenotic mitral flows. They are recorded in a new
question, q_audit_variant_residuals (unexplained_difference, questions.yaml), alongside q_eq13_eq14
and q_table3_units.

Not re-checked here: the figure readings themselves (the next job's). One oddity for that job:
fig9b_qao_read and fig9b_qmi_read start with the same value (8.764 [-19.98, 37.51]).
