# sexton2025 reading log

## First reading (boxgraph-reader, 2026-11-09, batch 7)

- Read pp. 1-8 (article) and 9-81 (supplement: methods, figure captions, Tables S1-S6, references).
- Entered the tree-generation constants (Table S1), the CFD constants (Table S3, pp. 5, 21), the identity
  the paper states for Eq. S6, the tree sizes it grows in a cube (1000, Fig. 2E; 4000, Fig. S8), the
  acceleration claim and the build times beside it, and the cell-counting arithmetic of the viability assay.
- Models: Eq. S6 (murray_beta); Eq. S10 as printed, its beta^4 variant and the S1-S4 network it is said to
  combine (reduced_resistance_s10, reduced_resistance_s10_beta4, bifurcation_network); nu = mu/rho; pixels per
  cell; the acceleration factor; the released code's defaults (svv_defaults); and svv_tree, which grows trees
  with the released svVascularize (svv 0.0.57, run in the separate environment corpus/cardio/envs/sim) on the
  paper's constants and computes the branching statistics and the tree equations on them.
- Checked before building: a fixed seed does not repeat an svv tree (q_svv_nonrepeatable); svv's stored R*,
  ratios and flows satisfy Eqs. S3, S6, S9 and S10-with-beta^4 to machine precision, but its stored radii do
  not follow from its stored ratios (q_svv_radii); svv's default viscosity differs from Table S1
  (q_svv_viscosity); the printed Eq. S10 lacks the fourth power svv uses (q_s10_beta).
- Validations against schwarz2020 (area growth and symmetry of large bifurcations) and kassab1993 (Horton
  ratios), with what each comparison can and cannot mean in q_validation_schwarz and q_validation_kassab.
- Nothing in other records was changed.

## Audit (second reading, 2026-11-09)

- No transcription errors in data or models. Added Table S5's largest build/benchmark pair and Table S6's
  million-terminal times, with their comparisons (cmp_speedup_table_s5_max, cmp_t1e6_*). Added the question
  q_svv_seed_order: grow.py seeds the svv domain after build(), so the stated seed may never take effect.
  Details are in audit.md.

## 2026-11-09 figure pass

- Added figures.yaml (45 code-mode readings), figures/ (reading code), figures.md, one datum per reading,
  the printed Fig. 5P values as tables, the model balanced_tree_n2 with its run and added C0, four
  comparisons (cmp_fig2b_recompute, cmp_fig5f_cfd_vs_piv, cmp_fig5p_count_bars, cmp_fig5p_viability_bars),
  new quantities, and five questions (q_fig2b_scaling, q_fig2f_axis_label, q_fig5f_piv_sum,
  q_fig_s10_units_axis, q_fig2hi_points). Nothing existing was changed. figures/figs2.py and
  figures/figs2_readings.py are unused stubs left by this pass (no reading refers to them).
