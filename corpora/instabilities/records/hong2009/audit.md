# Audit of hong2009

A second reading against the page images (pp. 1-3). No pages or figures were rendered in this pass.

## Checked, no change

- Every datum in `data.yaml` matches the page image in its digits and page: eps_biot_printed 0.46 (p. 1),
  eps_exp_printed 0.35 (p. 1), eps_c_approx_printed ≈ 0.35 (p. 2, in the text and the Fig. 3 caption),
  eps_c_printed 0.35 (p. 2), lambda1_c_printed 0.65 (p. 3), ratio_crease_printed 2.4 (Eq. 5, p. 3),
  ratio_biot_printed 3.4 (Eq. 6, p. 3), eta_c_printed 2.4, eta_biot_printed 3.4 and eta_exp_printed 2.0-3.7 (p. 3).
  No exponents are involved, and none of the transcriptions has an error.
- Models plane_strain_stretch, gps_critical_ratio, gel_swelling_from_ratio and gel_critical_swelling match
  the printed relations on p. 3: lambda_1 = 1 - eps_c, Eq. 3 (lambda_1 = lambda_1'/sqrt(lambda_2),
  lambda_3 = lambda_3'/sqrt(lambda_2)), lambda_1 lambda_2 lambda_3 = 1, and the gel stretches
  lambda_1 = lambda_2 = eta^-1/3, lambda_3 = eta^2/3. I re-derived Eq. 4 from Eqs. 1 (with lambda_2^2) and 3,
  and it agrees.
- The references (1-15) match p. 3.

## Changes

- Added datum `eps_c_summary_printed` (p. 3): the summary's "compressed by 35%", unit percent. It is a printed
  restatement of the crease threshold that was not recorded. Added comparison `cmp_epsc_summary` (consistency
  with eps_c_printed).
- Added question `q_eq1_lambda2_cubed` (p. 1, Eq. 1, kind possible_error): the page image shows lambda_2^3 in
  Eq. 1, but Eq. 4 (p. 2) has lambda_2^2. No model uses Eq. 1, so I did not write a variant.
- Added question `q_singh_pipkin_argument` (p. 2, kind unstated_model): the paper says the agreement is "not
  fortuitous" and cites the 1/sqrt(2) and sqrt(2) folded-state stretches, but never links them to the number 0.35.

## Validator

- SOUND. One warning remains, and it is expected: `fig3_energy_curve` (p. 2) is never compared with a run. It is
  the finite-element output itself, which cannot be rerun (q_fe_not_rerun). It enters the record only as the input
  to crease_zero_fig3.

## Disagreements

- None with the first reader's judgements: the added zero-finding choice (q_zero_extrapolation), the
  non-rerunnable FE model, and leaving out the Singh-Pipkin stretches and the 50 x 50 L block size all stand.
