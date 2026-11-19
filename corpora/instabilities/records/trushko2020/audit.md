# Audit of trushko2020 (second reading, 2026-11-18)

Checked against the page images: pp. 5, 8, 9, 10, 30-38, 40. Figures were not read; that is the next job.

## Values in data.yaml
- Every printed value matches its page image in digits, sign, exponent, unit and page. The values checked: Table 1 (p. 10); Section 5 (p. 37); p. 8; p. 5; Section 1 (p. 30); Sections 6 and 8 (pp. 38, 40); and the Fig. 4J labels 0.06363 and 0.07437 (p. 9). No transcription error was found and none was corrected.
- Disagreement, not changed: `spring_ratio_s5`, `bending_ratio_s5` and `lambda_ratio_s5` (p. 37) are printed after "∼". The record drops the tilde, a choice the first reader noted. Logged as question `q_audit_ratio_tilde` (reading).

## Models
- `capsule_bending_rigidity`, `capsule_compressional_rigidity` (p. 37), `capsule_spring_s36` (Eq. S36, p. 37) and `compressional_from_s37` (Eq. S37 solved for λ/λcap, p. 37) match the printed forms. So do `critical_strain_s21` (Eq. S21, p. 33), `pbuckling_eq1` (Eq. 1, p. 8; Eq. S26, p. 35), `pressure_compressed_ring` (p. 8; Eq. S25, p. 35, with K/λR² neglected as the paper does), `water_flux_s1` and `lumen_sphere` (p. 30). So do `friction_force_scale`, `vertex_normalized_params` and `sim_pressure_s42` (Eq. S42, p. 40). Units are converted correctly in each.
- Eq. S21 is consistent with S11-S13 and S20 (pp. 32-33). By hand: S11/S12 satisfy S8, putting them into S10 gives the factor 30(5/2)^(2/3) of S13, and S13 = S20 gives S21. No change.
- `fold_elastica`: Eq. S28 and boundary conditions S29-S30 as stated on pp. 35-36, and P_B = F_B cos α / R (p. 37), match the model's equation string. Its scope (inextensible limit, reconstructed) is the first reader's choice and was kept.

## Added
- `lambda_text_p8` (p. 8): main-text λ = 0.15 ± 0.13 N/m. New comparison `cmp_lambda_s37_text` (reproduction).
- `P_folding_measured` (p. 5): measured folding pressure "between 50 and 100 Pa" for 1.5, 2 and 2.5% alginate. New comparison `cmp_P_eq1_measured_range` (validation of Equation 1 with the 2.5% values of Table 1). This is a closer condition match than the existing 1% comparison `cmp_P_eq1_measured`, which is kept.

## New questions
- `q_audit_ratio_tilde` (reading, p. 37): tilde dropped from three printed ratios; see above.
- `q_fig4e_equation_reference` (possible_error, p. 9): the Fig. 4E legend calls the threshold line "Equation S25"; the threshold is Eq. S21 (p. 34).
- `q_fold_force_notation` (reading, p. 36): "P_B R^3/K cos α" is ambiguous; the record's reading P_B R^3/(K cos α) agrees with pp. 35 and 37.

## Unstated inputs
- `added.yaml` is empty. No run uses an input the paper does not state. The two choices that could have been added inputs are recorded as questions: the middle of the force range in `run_sim_P` (`q_sim_pressure_range`), and the inextensible limit of the fold model (`q_fold_model_limit`). No change.

## Validation
- `boxgraph validate corpora/instabilities/records/trushko2020`: SOUND (0 errors, 0 warnings).
