# Audit of shi2013_ch5

This is a second, independent reading of `corpus/cardio/2013_Shi_ch5.pdf` (PDF pages 1-14) against the record. Figures were not re-read.

## Checked, no change

- **Table 5-1 (p. 8)**: I checked every datum against the page image: Rcu, Ccu, Lcu, hcu, Rct, Cct,
  Rcl, Ccl, Lcl, hcl, ms, As, kf, ke, hs, Ps0, Psa, CQci, CQco, Cco, Patm, ha, rho. Digits,
  exponents, trailing points ("25.", "0.", "100.", "250.", "1.e3") and units match the page as
  printed. That includes kf in mmHg·m·s and ke in mmHg·m, so neither is an OCR error. Cci (0.015
  ml/mmHg) is left out on purpose by the first reader (q_cci_unused).
- **T_period (p. 11)**: "1 s" matches. Psa = 100 mmHg is also printed on p. 9.
- **Pct_min_text, Pct_max_text, Qct_min_text, Qct_max_text, l_amp_text, l_offset_text (p. 12)**:
  "0 ~ 120 mmHg", "0 ~ 400 ml/s", "0.0065 m" and "about 0.0035 m" match the image.
- **bioreactor_eqs5_1_15 (pp. 5-7)**: I compared Eqs. 5-1 to 5-15 in `model.py` term by term with the
  page images: signs, the hydrostatic terms, the orifice laws with sqrt|Δ| (the OCR drops the square
  root; the image shows it), the valve conditions (≥ / <), Eq. 5-12, the Eq. 5-13 force balance,
  Eq. 5-14 and Eq. 5-15. All are as printed. The unit conversions (mmHg↔Pa, m³↔ml) are correct.
  Pint gives 1.5e4 mmHg·m = 2.0e6 N/m and 25 mmHg·m·s = 3333 N·s/m, as the record says.
- **air_pressure_eq5_12 (p. 7)**: as printed.
- **bioreactor_waveform**: uses the same integrator. Mapping the phase into the last cycle is a
  first-reader choice, already in q_solver_settings.
- **added.yaml**: g_added, ke_as_N_per_m and kf_as_N_s_per_m each have a basis and real
  alternatives. The alternative for ke/kf is the printed-unit value, which is also run (run_printed).
  The initial state, dt and the number of cycles are settings, recorded in q_solver_settings.
- **source.yaml**: `reader.model` is `None`. This is first-reader metadata and I left it unchanged.

## Transcription errors corrected

- None found.

## Added

- **q_amplitude_definition** (reading, p. 12): the chapter does not define "amplitude" or "neutral
  position" for l. The record's half-range / mid-range reading is one of several, and the verdicts on
  l_amp_text and l_offset_text depend on it.
- **q_flow_phase_claims** (reading, p. 13): the chapter states model results in words that are not
  compared: Qcl, Qct and Qco are zero while Qs < 0; Qci is zero while Qs > 0; Pcl and Pct exceed Ps
  while Ps rises and are clipped late in its fall. Comparing them would need new model outputs. I did
  not add any, because editing the models is the first reader's scope and would invalidate the
  cached runs.

## Disagreements

- None beyond the two reading questions above.
