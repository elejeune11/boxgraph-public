# Audit of liu2025 (second reading)

Checked against the page images: Methods Eqs. 1-11 (pp. 19-23), Results numbers (pp. 12-14),
Appendix A Eqs. A9-A13 (p. 38), Appendix C Eqs. C1-C10 (pp. 41-42), Appendix E (p. 43),
Tables T1-T4 (pp. 55-58), Extended Data Fig. 1, 3 and 5 legends (pp. 30-31, 70) and Extended Data
Table 2 (p. 79). Figures were not read (next job).

## Values in data.yaml

- No transcription errors found. All Table T1 values (kon_KD, kon_WT, k0off "5.4 x 10^-5", k0offp,
  xt, xtp "-0.11", v0, Fst, sm_KD, sm_WT, sc, kc_KD, kc_WT, r_KD, r_WT, R_FA, ly_KD, ly_WT_bound;
  p. 55) agree with the page image, and with Extended Data Table 2 (p. 79).
- sm_KD_bleb15, sm_KD_bleb50, sm_WT_bleb15, sm_WT_bleb50 (p. 70): the panel labels read 43, 26, 41, 24.
- sm_cusp_printed (p. 13), bistab_ratio_printed (p. 14), F_5pN, F_10pN, dx_folded, dx_vinculin,
  v_rigid_talin, rate_folded_printed, rate_vinculin_printed (p. 12), ec_circle, Ie_circle_printed
  (p. 38): agree.

## Models

- steady_linear (pp. 19-23): Eqs. 1, 4, 5, 8, 9, 10, 11 are implemented as printed (signs and the
  4 pi r E / 9 factor; Eq. 4 with |F| in both exponents; Eq. 9's denominator). No change.
- fc_v_C10 (p. 42): Eq. C10 as printed, including the Meijer G index layout G^{3,0}_{2,3}(0,0; -1,-1,-1).
  I re-derived C10 from C8 and C6 and it is consistent with them. No change.
- Ie_A11, Ie_A13 (p. 38): as printed. A13 follows from A11 with A12. No change.
- cusp_sigma_m, loading_rate_text, talin_wt: as described. No change.

## Additions

- Data, p. 55: talin WT column of Table T1 (kon_talinWT, sm_talinWT, r_talinWT, L_linker, Lp_chain,
  Ng_talin, b_domain, ku0_R3, Fu_R3, kf0_R3, alpha_talinWT). These were not recorded before. The talin model
  is not runnable here, so I recorded them for checking the liu_code parameters.
- Data, p. 56: Table T2, WT-2 model (kon_WT2_nontalin, kon_WT2_talin, sm_WT2, kc_WT2_nontalin,
  r_WT2_nontalin, r_WT2_talin, ly_WT2_nontalin).
- Data, p. 58: Table T4 (konv0, kon_R3v, koff_R3v, alpha_vinculin = 2.6 from the footnote).
- Data, p. 57: Table T3 k_talin_rod (0.12), k_talin_rod_linker (0.09, "estimated based on the WLC
  model"), F_range_10pN.
- Model talin_linker_wlc (p. 57; reconstructed, from_words), run_talin_linker_wlc and
  cmp_talin_rod_linker: Table T3's 0.09 pN/nm was a printed derived result with no check. A
  Marko-Siggia WLC (L = 37 nm, Lp = 1 nm) in series with the 0.12 pN/nm rod at 10 pN gives 0.093.
  The result is the same with kBT at 298 K. See the question q_wlc_estimate.
- Model density_ratio, run_ratio_fitted_KD, cmp_bistab_ratio_fitted (p. 14): a consistency check of
  "≳1.6 times" against the two fitted densities it refers to (71/43 = 1.65). The first reader's
  cmp_bistab_ratio (71 over the computed cusp density) is unchanged.
- References: si-ref-18, si-ref-27, si-ref-28, si-ref-32 (pp. 60-61), cited by the new data.
- Quantities for the new data (protein_average_stiffness, wlc_contour_length, persistence_length,
  talin and vinculin kinetic quantities).

## Disagreements and new questions

- q_fig_S1_linear (p. 49, reading): Fig. S1(a,b) plots the linear KD and linear WT clutch density and
  tension. These are outputs n_on and F1 of steady_linear. figures.md leaves them out, but the figure
  job should read and compare them.
- q_ed3_kc_threshold (p. 31, unstated_input): Extended Data Fig. 3 gives two bistability thresholds:
  kc > 2.6 pN/nm, and E > 2 MPa at kc = 5 pN/nm. Both rest on the 1 ug/ml fit parameters, which
  appear only as points in Fig. 3(c), so they are not checked yet.
- q_wlc_estimate (p. 57, unstated_model): the WLC estimate of Table T3 is not specified.
- No disagreement with the added inputs. kT_310K, ly_WT and S_FA have a basis and real alternatives.
  The first reader's q_ly_WT and q_sm43_bistable cover the doubts I would have raised.
