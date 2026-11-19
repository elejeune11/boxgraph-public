# Audit of wang2014 (second reading)

Every datum in `data.yaml` was checked against the page images (pp. 2, 4, 5, 6, 7, 8, 9), and every model
against the printed equations (Eqs. 1-8 on pp. 3-6).

## Values checked and found as printed

- `mu_s_ecoflex` (p. 2) 10.4 kPa; `mu_f_sylgard_range` (p. 2) 6.7 to 155 kPa: correct.
- `eps_crease` (p. 6, "a constant, 0.35"; p. 4 "≈ 0.35"); `ew_max_printed` (p. 4, "around 0.465"): correct.
- `mu_b_lp1/2/3` 1.54, 1.22, 1.14 (p. 7); `triple_mu_lp1` 1.54, `triple_gamma_lp1` 0.77 (p. 7, also Fig. 6(b)
  label); `triple_gamma_lp2` 0.73, `triple_gamma_lp3` 0.39 (Fig. 7 labels, p. 5): correct.
- `gamma_044`, `mu_ratio_2`, `ec_buckle_example` 0.28, `D_buckle_example` 10.2 (p. 6): correct.
- `pd_min_mu_ratio` "≥ 10" (p. 8, OCR drops the ≥): correct.
- `lam_p_*`, `mu_ratio_1` (pp. 4, 7): correct.

## Models checked

- `eq5_stiff_film` (p. 4, Eq. 5): matches the printed equation, including the printed Lambda = (1 + lambda_p^2)
  without the factor 1/2. `eq5_stiff_film_half` is the first reader's corrected variant, kept beside it with
  `q_eq5_lambda`; no change.
- `wrinkle_linear_stability`, `wrinkle_crease_boundary`: the paper prints no equations for them (p. 3, "Following
  Cao and Hutchinson"; p. 6, intersections of the curves of Fig. 6(a)); the strain convention used (film stretch
  1 - e, substrate stretch lambda_p (1 - e)) agrees with Eq. 3 (p. 3). No change.
- `fe_delaminated_buckling` (p. 6, Eqs. 6-8): equations transcribed correctly. No change.

## Changes

- `H_f_range` (p. 2): corrected the transcription "21 to 583" to "~21 to ~583"; the page prints both ends with a
  tilde ("from ∼21 to ∼583 μm").
- Added `mu_f_sylgard_2pct`, `mu_f_sylgard_3pct`, `mu_f_sylgard_4pct`, `mu_f_sylgard_5pct` (p. 9, Fig. 13 panel
  labels 6.71, 38.2, 102.8, 155.1 kPa): printed individual film moduli, which the first reading said appear
  only as labels; they are printed text, so they are data for validation jobs. Updated the note of
  `mu_f_sylgard_range` accordingly.
- Added `triple_mu_lp2` (1.22) and `triple_mu_lp3` (1.14) (p. 5, Fig. 7(a), 7(b) labels) and comparisons
  `cmp_triple_mu_lp2`, `cmp_triple_mu_lp3` against the existing boundary runs, as was done for lambda_p = 1.
- Added `adv_pd_fold_gamma_lp1` (1.19), `adv_pd_fold_mu_lp1` (10), `adv_ridge_gamma_lp2` (1.13),
  `adv_ridge_mu_lp2` (1.24) (p. 8, Fig. 12 labels), with new quantities `advanced_boundary_point_adhesion` and
  `advanced_boundary_point_modulus_ratio`; finite-element results, not rerunnable (question `q_adv_points_fe`).
- Added question `q_ridge_point_vs_boundary` (p. 8): the label 1.24 at lambda_p = 2 versus the initial
  wrinkling-creasing boundary 1.22.

## Disagreements (recorded as questions, not changed)

- `q_experiments_on_diagram` (p. 7, Fig. 7(a), p. 5): the experimental points on the lambda_p = 2 diagram are
  validation data and should be read by the figure job, not left out as categorical.

## Noted, not recorded

- Fig. 5(e) (p. 4) labels the applied strains of optical images of a delaminated buckle (0.127, 0.156, 0.159,
  0.159); the film modulus, thickness and adhesion of that specimen are not given, so they cannot be placed on
  a diagram.
- Experimental settings on p. 2 (substrate thickness over 5 mm, relaxation rate 1 x 10^-3 1/s, peel rate
  1 x 10^-4 m/s) and neo-Hookean validity limits on p. 3 (stretch 2.5 Ecoflex, 2.2 Sylgard) feed no model.
