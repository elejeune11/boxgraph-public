# Audit of kassab1993

Second, independent reading of `corpus/cardio/1993_Kassab.pdf` (PDF pages 1-16) against the record,
2026-11-06. Figures were not read (left to the next job).

## Values checked against the page images (no transcription errors found)

- Tables 1-3 (p. 9): every segment and element mean diameter and length of the RCA, LAD and LCX
  (sD_*, sL_*, eD_*, eL_*), including the order 11 (10 for LCX) cells printed without an SD, agree
  with the page image in digits, decimals and units (um for diameter, mm for length). The SDs in
  `note` agree too.
- Table 4 (p. 10): all 96 constants (t4_*) agree, including the positive printed b of "Total no."
  (already a question, q_number_slope_sign).
- Table 5 (p. 10): all S/E means (SE_*) agree; the OCR "2.00t0.9 1" for RCA order 5 is 2.00 ± 0.91
  on the page, as recorded.
- Table 6 (p. 11): every component C_rca_m_n and every SE Cse_rca_m_n agree, including column 11
  (0, 1, 11, 8, 5, 6, 0) and row 5, column 10 (0.727 ± 0.304).
- Table 9 (p. 12): every element number N_rca_*, N_lad_*, N_lcx_*, N_wh_* agrees (LCX order 7
  is 144 ± 4, as the first reader noted; LAD order 1 SE 221,134 is split by OCR but recorded
  correctly in the note).
- Table 10 (p. 14): the Intact and Cut columns (t10_intact_*, t10_cut_*), the Extrapolated column
  (t10_extrapolated) and the Corrected Total with its SEs (t10_total, t10_total_se) agree.
- Discussion (p. 13): vol_rca 1.4 ± 0.15, vol_lad 0.98 ± 0.21, vol_lcx 0.57 ± 0.09 ml;
  n9_from_10_text 24, n9_from_9_text 2; elements_heart_text 1.4 x 10^6 all agree.

## Models checked against the printed equations (no transcription errors found)

- horton_*_fit_* (Eqs. 2, 4, 5, pp. 9-10): log10 y_n = a + b n by least squares, as printed.
- ratio_from_b_* (Eq. 3, p. 9): ratio = 10^b, as printed.
- tree_volume_10/11 (Eqs. 6a, 7a, p. 11): A_n = (pi/4) D_n^2 N_n, V_n = L_n A_n, summed over orders,
  as printed.
- extrapolation_eq10 (Eqs. 10, 11, p. 15): summation from m = n to 11 with C(n, m) in row n, column m,
  and the linear (not quadrature) error sum of Eq. 11, as printed. The treatment of the m = n term is
  the first reader's reading (q_eq10_diagonal); not changed.
- connected_elements (p. 13): C(m, n) N_n as in the text before Eq. 9.
- The definition of the matrix in Matrix description of branching pattern (p. 7: "row n and column m
  is the ratio of the total number of elements of order n sprung from elements of order m") supports
  the orientation the first reader chose in q_table6_orientation; not changed.

## Additions

- txt_D_ratio_e_rca, txt_D_ratio_e_lad, txt_D_ratio_e_lcx, txt_L411_ratio_e_rca, txt_L411_ratio_e_lad,
  txt_L411_ratio_e_lcx, txt_L13_ratio_e_rca, txt_L13_ratio_e_lad, txt_L13_ratio_e_lcx (p. 10): added
  the element diameter and length ratios printed in the Results text (1.81, 1.84, 1.89; 2.12, 2.02,
  2.20; 1.19, 1.14, 1.14), with comparisons cmp_txt_* against the existing fit outputs
  fit_*_ratio_e_*.
- t9_rca_total and t9_rca_se (p. 12): added the RCA column of Table 9, with its SEs, as curves. The
  paper says on p. 10 that Table 9 is computed from the connectivity matrices by the APPENDIX method.
  It is now compared with the Eq. 10 and 11 run outputs (cmp_eq10_table9_rca with t10_total_pred,
  cmp_eq11_table9_rca_se with t10_total_se_pred). The scalar N_rca_* data are kept as they were.
- q_eq9_index (p. 13, possible_error): Eq. 9 multiplies by N_m, but the text before it gives C(m, n) N_n.
- q_eq10_text_range (p. 15, possible_error): the text says "m is equal or smaller than n", which
  contradicts the summation m = n..11 of Eq. 10.
- q_eq11_table_numbers (p. 15, possible_error): the text says the SEs of "Tables 7-9" are used as
  dC(n, m), but the connectivity matrices are Tables 6-8.

## Unstated inputs

- The record has no `added.yaml`, and I found no assumed value. The units of the log10 fits (um) and
  the choice of element means and Table 9 numbers for the volume sum are readings, recorded as
  q_horton_units and q_volume_rca. I agree with them as recorded.

## Disagreements

- None that needs a `reading` question. The only printed results still left out are the
  3.0 x 10^6 arterial segments (p. 13), which need the S/E of the LCCA trunk, and the LAD, LCX and
  whole-heart columns of Table 9 (q_table9_other_columns). Both are left out for reasons the first
  reader stated, and I agree with them.

Validator: `.venv/bin/boxgraph validate corpora/cardio/records/kassab1993` gives SOUND (0 errors).
The 43 warnings are the scalar Table 9 numbers that no run is compared with; they were there before
this audit.
