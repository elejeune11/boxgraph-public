# Audit of kim2010

Second reading of `corpus/cardio/2010_Kim.pdf` against the record, page images checked for every recorded number.

## Checked, no change

- All 120 Table 3 resistance data (`Ra_*`, `Ram_*`, `Rv_*`, rows a-k at R and E1, rows c, d at E2, stenosis rows c*-c****, d*-d**** at R and E2), p. 7: every value matches the page image; unit 10^3 dynes s/cm^5 = kdyn*s/cm^5 is right.
- Table 4 flows and pressures (`Q_lad_*`, `P_lad_*`), p. 10: all twenty values match the image.
- Text values `Tc_rest`, `Tc_E1`, `CO_rest`, `CO_E1`, `Psys_rest`, `Psys_E1`, `SV_rest`, `SV_E1`, `psys_increase_E1` (p. 6), `coronary_fraction` (p. 4), `coronary_increase_E2` (p. 5), `Q_LAD_rest` ... `Q_total_E1` (p. 7): all match.
- Models `stenosed_lad_flow`, `coronary_flow_split` against Eq. 5 coefficients p0 = 1, q0 = Ra + Ra-micro + Rv + Rv-micro (p. 4, image): correct steady limit, unit conversions correct (mmHg -> dyn/cm^2, kdyn -> dyn).
- Models `cardiac_output_sv`, `coronary_fraction_flow`, `coronary_total_sum`, `systolic_increase`, `coronary_increase_by`, `coronary_increase_to` (pp. 4-7, 13): match the words; unit factors correct.
- `Pv_added` (added.yaml): basis given and alternatives 5 and 10 mmHg are real alternatives that move verdicts; no change.
- No transcription errors found; nothing corrected.

## Added

- Model `contractility_increase`, data `ELV_max_R`, `ELV_max_E2` (Table 1, p. 6) and `contractility_increase_E2` (p. 10), quantities `max_lv_elastance` and `contractility_relative_increase`, run `run_contractility_E2`, comparison `cmp_contractility_E2`: the paper states contractility was raised 10% for moderate exercise (p. 3204) and Table 1 prints E_LV,max 2.0 (R) and 2.2 (E2) mmHg/cc; this printed result was not compared.
- Question `q_table2_G_rest_exercise` (possible_error, p. 6): Table 2 left subclavian Rp is 1.80 at rest and 1.08 in light exercise although the note says the upper branch parameters are unchanged.
- Question `q_heart_rate_tripled` (unexplained_difference, p. 5): "tripled ... heart rate" vs the 0.3 s moderate-exercise cycle of Table 1 (factor 3.33).
- Question `q_moderate_coronary_rule` (unexplained_difference, p. 4): the 4.0%-of-cardiac-output rule for exercise vs the 350% increase at moderate exercise with tripled cardiac output.
- `source.yaml` notes: one sentence pointing to this audit.

## Disagreements (not changed)

- None that change a verdict. Note only: `coronary_increase_to` is filed as a `variant_of` (a corrected misprint) although the "by"/"to" ambiguity is one of wording, not of a printed equation; its evidence (Table 4, p. 10; "tripled", p. 11) is stated and the question `q_increase_350` records the doubt, so it is left as the first reader chose.
