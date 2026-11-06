# Audit of reymond2009

Second, independent reading of `corpus/cardio/2009_Reymond.pdf` against the record by an agent, 2026-11-04. No figures were rendered or read.

## Values checked, no change needed

- Table 2 (p. 6), all 73 segment entries (dp_*, dd_*, D_*, va_*, RT_*, CT_*): checked row by row against the page image
  and the text layer. Every digit agrees, and every L/R split is assigned to the right side. Shared cells (e.g.
  dd_s10_24 = 1.8, va_s8_22, RT/CT of Radial and Ulnar B) are entered once, as printed. No transcription error.
- Table 2 header units (p. 6): "10^-3 l/mmHg" and "10-5 ml/mmHg", recorded as 1/meter_Hg and ml/hectometer_Hg. Both
  factors are right (1 m = 10^3 mm, 1 hm = 10^5 mm). Agree with q_table2_units.
- a2 = 13.3, b2 = 0.3, rho = 1050, a3 = -0.0062 mm^-1, b3 = 0.16, b3_cerebral = 0.34, P_csf = 15 mmHg (p. 5): agree with
  the page, sign of a3 included.
- r1_fraction_range "0.05 to 0.4" (p. 3): agrees.
- kappa = 0.0005 s/ml (p. 6); V0 15 ml, Emin 0.08, Emax 2.6 mmHg/ml, P_end_dia 14 mmHg, R_ven 0.003, heart_rate 75 bpm,
  t_max 340 ms (p. 7): agree.
- Table 4 systolic and mean flows, Table 5 systolic, diastolic and pulse pressures (p. 9): all 54 entries agree with the
  page image.
- Discrepancy statistics 22 ± 16, 12 ± 11, 9 ± 6, 12 ± 5 % (p. 8): agree.
- Table 6 (p. 12), all 48 entries: agree with the page image.

## Models checked against the printed equations, no change needed

- distensibility_eq22_eq6: Eq. 22 PWV = a2/d^b2 (p. 5) and Eq. 6 C_A = A/(rho PWV^2) (p. 3). As printed. The
  mean-diameter construction is the first reader's choice (q_mean_diameter). Spot check s1: 5.45 against 5.46 printed.
- viscoelastic_eq9: Eq. 9 ã ≅ a3·d̄ + b3 (p. 3), as printed.
- r1_minimal_reflection: ZC = rho·PWV/A and R1 = ZC (p. 3), as printed.
- terminal_compliance_eq15: Eq. 15 C_Ti ≅ C_T C_A^i / Σ C_A^i (p. 3), as printed. Scaling from the radial bed is the
  first reader's construction.
- pulse_pressure: PP = Psystole - Pdiastole (p. 7), as printed.
- arterial_tree_1d (not runnable): the equation summary agrees with Eqs. 1-21 (pp. 2-4).
- discrepancy_* and table6_relative_*: processing of the paper's own numbers. Their normalisation choices are the first
  reader's (q_discrepancy_norm, q_table6_reference_row).

## Additions

- quantities `diastolic_flow_rate` and `mean_pressure` (quantities.yaml): needed by the new data.
- qdia_vivo_* / qdia_model_* (18 data, p. 9, Table 4 "Diastolic Flow Rate"): the column the first reader left out,
  added as measured and predicted values, signs as printed (e.g. qdia_model_asc_aorta "-33"). The in vivo values are
  validation data for other papers' models. The model values come from the non-runnable 1-D model and stay uncompared,
  as its other outputs do.
- pmean_vivo_* / pmean_model_* (6 data, p. 9, Table 5 "Mean Pressure"): the column the first reader left out.
- model `mean_pressure_dia_pp` (p. 7): the printed rule "Pmean ≅ Pdiastole + 1/3 PP". The record did not compare it.
  Runs run_pmean_vivo_radial, run_pmean_vivo_cca, run_pmean_vivo_temporal take Table 5's in vivo diastolic and pulse
  pressures. Comparisons cmp_pmean_vivo_* (purpose approximation, with conditions_ok) check them against Table 5's in
  vivo means. Results: 86.7 against 87 (radial), 79.0 against 85 (CCA), 82.7 against 87 (temporal).
- question q_pmean_one_third (unexplained_difference, p. 7): the CCA and temporal in vivo means do not follow the
  one-third rule. In addition, a single brachial calibration would give equal mean and diastolic pressures at the three
  sites, but the printed values differ.
- question q_table3_vs_table4_cerebral (unexplained_difference, p. 7, Table 3): Table 4's in vivo ICA (3.6) and MCA
  (2.5) mean flows differ from the paper's own ultrasound row in Table 3 (ICA 3.7/4.5, MCA 2.2), read from the page
  image because the OCR misaligns the columns. The MCA value equals Table 3's "Mean flow rate chosen". Table 3 itself
  stays unrecorded (the first reader's scope).
- source.yaml notes: added a paragraph on the audit and removed "the diastolic flow and mean pressure columns" from
  the "Left out" list.

## Disagreements and remarks (no change made)

- source.yaml `reader.model` is `None`. This is the first reader's metadata, left as it is.
- Table 3 (p. 7) is left out by the first reader. Its "Mean flow rate chosen" row sets the cerebral WK3 resistances
  and could be recorded as `reported` inputs. I agree it has no runnable model, so I added no `reading` question.
- No other unstated inputs were found. added.yaml has one entry (w_norm_added), which has a basis and alternatives
  0 and 1. The remaining constructions (mean diameter, R1 diameter, CT reference bed, Eq. 15 distensibility) are
  recorded as `choice` questions.

Validator: `SOUND (0 errors, 66 warnings)`. All warnings are printed outputs of the non-runnable arterial_tree_1d.
