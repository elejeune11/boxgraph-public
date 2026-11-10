# sexton2025 audit (second reading, 2026-11-09)

Checked against the page images: pp. 1, 3, 5, 11, 12, 34, 35, 67, 69, 71, 72; text of pp. 2, 4, 6, 51, 57.

## Values (data.yaml): no transcription errors found

- gamma_t1, alpha_r_t1, alpha_l_t1, mu_t1 (p. 67, Table S1): 3, 2, 1, 4 cP. Match.
- mu_t3, rho_t3, nu_t3 (p. 69, Table S3): 4 cP, 1.06 g/cm3, 0.037 ("cm · s"). Match. Table S3 also prints
  solid density 2.00 g/cm3 and body forces 0; no model uses them, so they were not entered.
- rho_p5, mu_p5 (p. 5): "ρ = 1.06 g/cm3 and ν = 0.04 cP". Match.
- gamma_range_lo (p. 11): "2 ≤ γ ≤ 3". Match.
- murray_identity (p. 12): "∑ β_i^γ ≡ 1". Match.
- n_term_1000 (p. 3), n_term_4000 (p. 51). Match.
- speedup_abstract (p. 1): "230-fold". t_gyrus_8000_new, t_gyrus_8000_ref (p. 3): 15 min, 59.96 hours. Match.
- area_live (p. 34) 207.9 um2; area_dead, pixel_res, px_live, px_dead (p. 35): 220.4 um2, 5.524 um/pixel,
  6.813, 7.223. Match.

## Models: no transcription errors found

- murray_beta: Eq. S6 (p. 12) as printed. Match.
- reduced_resistance_s10: Eq. S10 (p. 12) as printed, with beta_k to the first power and the first term
  8 mu L_i / pi. Eq. S9's ratio (R*_j Q_j / R*_i Q_i)^(1/4) and Eq. S6's ratios are as printed. Match.
- reduced_resistance_s10_beta4: the variant is justified. The evidence it cites holds:
  svv/tree/utils/c_update.py lines 35-37 use beta^4, and lines 32-34 compute the ratios by Eqs. S9 and S6.
- bifurcation_network: Eqs. S1-S4 and S7 (p. 11-12). Match.
- kinematic_viscosity, pixels_per_cell, speedup: the arithmetic the pages describe. Match.
- svv defaults cited in added.yaml and q_svv_viscosity (svv/tree/data/data.py lines 263-278: nu 0.036,
  rho 1.06, Q 0.125/2000, 60 and 100 mmHg). Match.

## Added (printed results not compared before)

- t_globus_pallidus_build, t_globus_pallidus_bench (p. 71, Table S5) are new data, with
  run_speedup_table_s5_max and cmp_speedup_table_s5_max against speedup_abstract (p. 1). This is the largest
  of Table S5's twenty benchmark-to-build ratios, so every other ratio is smaller. It backs q_speedup's
  statement, which no datum supported before.
- t_biventricle_1e6, t_annulus_1e6 (p. 72, Table S6) and t_1e6_text (p. 4, "about 5 hours") are new data,
  with cmp_t1e6_biventricle and cmp_t1e6_annulus. The main text's time is approximate ("~5"), so these
  comparisons get no verdict. They record that the main text and Table S6 agree.

## Disagreements and new questions

- q_svv_seed_order (reading; about q_svv_nonrepeatable, svv_tree): the model's grow.py sets the domain's
  seed after Domain.build(), and build() has already made an unseeded generator
  (svv/domain/domain.py lines 179-190, 460-461). So the stated seed never reaches the generator that
  places the terminals, and the non-repeatability may come from the script, not from svv. Not tested here:
  this job could not run the sim interpreter directly. grow.py was left unchanged, because an edit would
  rerun every tree, and the first reader's choice stands until a test shows otherwise.

## Considered and not entered

- p. 4, "At 1 million outlets, vessel diameters ranged from 1.2 mm to 5 μm". By Eq. S5 applied down the
  tree, the cube-mean terminal diameter is d_root N^(-1/3), which is 12 um. A smallest diameter of 5 um is
  consistent with that, so there is no doubt to record, and the result is organ-scale (q_organ_scale).
- p. 6, the viability results (417-fold, 37.8 %, 0.4 %) are measurements that no model in the record
  produces.
- Figures (Fig. 2B-C, F, H-I; Fig. 3; Figs. S1, S8, S10) are left to the figure job.
