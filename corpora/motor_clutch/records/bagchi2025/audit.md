# Audit of bagchi2025 (second reading, 2026-11-21)

Checked against the page images: every value in `data.yaml` that is typed in (S1 Table p. 39,
S2 Table p. 41, S3 Table p. 42, Fig 10l/11l legends and captions pp. 20-21, ratios pp. 16, 19,
28, experimental conditions pp. 3, 12, 23), and every model against Eqs 1-8 (p. 27), 10 (p. 29),
11-12 (p. 30), 13 (p. 31), 14 (p. 32). Figures were not re-read (next job).

## Transcription check: no errors found

- S1 Table (p. 39): Fp_s1 3083 nN, kc_s1 4.92, eta_c_s1 0.55, kl_s1 18.51, eta_l_s1 0.22,
  ks_s1 6.17, eta_s_s1 0.22, kcl_s1 30.86, kls_s1 12.34: all as printed, units as printed.
- S2 Table (p. 41): all twelve values as printed, including exponents 10^-71, 10^-5, 10^-3.
- S3 Table (p. 42): all twenty-four values as printed; delta_eta_conn is printed 1.75*10^-711
  on the page image, as recorded (question q_delta_eta_711 already open).
- alpha_c1..c6 (p. 20, Fig 10l legend 0.08, 0.04, 0.02, 0.01, 0.006, 0.003) and
  kmin_c1..c5, kmax_fig11 (p. 21, Fig 11l legend and caption): as printed.
- t_rest_conn/disc (p. 28), v_ratio_fig9/T_ratio_fig9 (p. 19, printed with a superscript
  asterisk, read as approximate by the first reader: kept), v_ratio_s4/T_ratio_s4 (p. 16),
  gel_E_soft_* (pp. 12, 23), align_time_* (pp. 3, 23): as printed.
- Models: threshold_strain_eq10, cell_stiffness_eq11, cell_damping_eq12 match Eqs 10-12 term
  by term (signs: Eq 10 and 11 subtract the Gaussian, Eq 12 adds it and subtracts delta).
  binding_prob_eq13 is Eq 13 as printed, tan^-(alpha(-x_c) + 1.5)/3; the variant
  binding_prob_eq13_shifted is beside it, not instead. substrate_stiffness_eq14 matches Eq 14.
  chain_eqs1_8 transcribes Eqs 1-8 correctly (including eps_c,i in Eq 6).

## Additions

- references.yaml: added ref-48 (Chan & Odde 2008, p. 36), linked to record chan2008; cited
  on pp. 8 and 30 for actomyosin contractility only.
- data.yaml: added v_ratio_s4_p30 and T_ratio_s4_p30 ("twice", "two times lesser", p. 30),
  the S4 Fig ratios restated in the Methods; t_stall_results (p. 16) and t_stall_methods
  (p. 29), the ~5 h stall of the simulation without fluidization.
- quantities.yaml: added stall_onset_time.
- comparisons.yaml: added cmp_v_ratio_s4, cmp_T_ratio_s4 (p. 30 vs p. 16) and cmp_t_stall
  (p. 29 vs p. 16), all consistency; the "~" side gives no verdict.
- questions.yaml: q_ligand_stiffness_claim (p. 28 vs p. 39): the paper's argument needs
  k_l >> k_l-s and k_l >> k_c-l, but S1 gives 18.51 vs 12.34 and 30.86.
- questions.yaml: q_s2_sigma_k (p. 41): S2 delta_k = 1.75e-71 is the sigma = 1 Gaussian at
  18 nodes, not the sigma = 10 one printed for sigma_k; delta_eps values follow a different
  rule (Gaussian / gamma_eps).
- questions.yaml: q_eq11_negative (p. 42, Eq 11 p. 30): the S3 disconnected set gives negative
  cell spring stiffness at the centre (-6.7 at x = mu; -2.7 at nodes 18-19 for mu = 18.5).
- questions.yaml: q_net_elasticity (p. 32): the "roughly the same net elasticity" claim against
  Eq 11 with the S3 sets (summed stiffness 13300 vs 18500).
- questions.yaml: q_fig11h_axis (p. 21): Fig 11h time axis "Time (hr)" runs 0-2000, the other
  panels 0-5.

## Disagreements with the first reader (recorded as `reading` questions, nothing changed)

- q_s1_refs (p. 39): its "every S1 stiffness is a simple multiple of 6.17" is only approximate
  for k_c (0.797x) and F_p (499.7x, and F_p is in nN, not nN um); recorded as q_audit_s1_multiples,
  which also notes chan2008's clutch stiffness 5 nN/um is close to bagchi's k_c, not k_c-l,
  with no stated provenance.
- q_ratio_statements (pp. 5, 12, 16, 30): the experimental 1.34 (p. 12) is for the double
  negative condition, not the same ratio as 1.56 (p. 5); recorded as q_audit_speed_ratios.

## Not changed

- No limit of the chain returns chan2008's single substrate spring that the paper states, and
  the chain is not runnable, so no reduces_to relation is recorded; relations.yaml stays empty.
- Added inputs (mu_36, mu_37, n0_ligand, xmax_substrate) each have a basis and alternatives.
