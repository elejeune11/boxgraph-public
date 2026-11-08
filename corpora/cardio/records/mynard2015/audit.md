# Audit of mynard2015

A second, independent reading of the paper (PDF pp. 1-18) against the record, made from the page images of
pp. 2-8 and 11 and the text of every page that has a number. Figures were not read; the next job reads them.

## Values checked (data.yaml)

- Eq. 3 and Table 2 (p. 6): `rho_blood`, `k1_*`, `k2_*`, `k3_*` and the lower ends of the c0 ranges
  (`c0_min_sys_art`, `c0_min_pulm_art`, `c0_min_cor_vein`) agree with the page. The minus signs of k2
  (-9, -7, -22.5) and the powers of ten in the column headers (10^6, 10^4) are right. No change.
- `d_cs_model` 0.79 cm, `d_cs_human` 0.81 (no unit printed) (p. 6): agree. No change.
- `alpha_sip` 8.2 mL, `sip_ratio_max_claim` 20% (p. 7): agree. No change.
- Table 3 (p. 7), `comp_*`: agree (170, 1.7, 146, 6.7, 15.8). The row "Liver 54" is not recorded as a datum.
  It sits inside "Systemic veins (incl. liver)" and feeds no check. Not added.
- Table 4 (p. 7), `vp0_lv`, `vt0_*`, `mu_av_la`, `mu_av_ra`: agree. No change.
- Pericardium (p. 8), `k_pc`, `v0_pc`, `phi_pc` (no unit printed), `v_pcf`, `v_myo`, `ppc_normal_claim`: agree.
  No change.
- Table 6 (p. 7), model and reference columns, all 24 rows: agree, including the signs of -2200, -2296 and -232
  that the OCR prints as "22200", "22296" and "2232". No change.
- Table 8 (p. 11), the four recorded rows (LV Emax -50%, RV V0 +150 mL, kappa = 0, mu = 0) x 8 columns: agree,
  with every sign checked against the image. No change.
- Text claims on Table 8 (p. 11), `claim_*`: agree. No change.

**I found no transcription errors and made no corrections.**

## Models checked against the printed equations

- `wave_speed_eq3` (p. 6, Eq. 3): matches c0^2 = 2/(3 rho) [k1 exp(k2 D0/2) + k3]. No change.
- `sip_ratio_eq1` (p. 3, Eq. 1): matches pSIP = alpha_SIP pV/(vV - Vp=0,V), divided by pV. No change.
- `pericardial_pressure_t5` (p. 2, Eq. T5; p. 8 for vpc): matches ppc = Kpc exp[(vpc - V0,pc)/Phi_pc], with vpc the
  sum of the chamber volumes, the pericardial fluid volume and the myocardial volume. No change.
- `mu_av_left_from_right` (p. 7): matches "2/3 of the right atrial value". No change.
- The units of mu_AV (g/cm^7/s) agree with Eq. T6 (p. 2), where mu_AV q_V is an elastance. No change.
- `compliance_sum`, `cardiac_output_from_ef`, `min_volume_from_ef`, `vascular_resistance`, `abs_range_8`: these are
  definitions taken from the paper's words (from_words), and their code is right. No change.

## Results not yet compared

- The upper ends of the Table 2 c0 ranges (p. 6) need each network's smallest D0, which is in Supplemental
  File 1 only. As a side check, every printed range lies inside the bounds Eq. 3 allows,
  sqrt(2 k3/(3 rho)) to sqrt(2 (k1 + k3)/(3 rho)). This holds for all six networks. Nothing added.
- The Table 2 literature reference wave speeds (441 AoRt, 115 IVC, 260 RPA, 860 LAD) are left out by the first
  reader. The model's c0 at those locations needs diameters that are only in the supplement. I agree; nothing added.
- I found no other printed result from a runnable part of the model. The remaining Table 8 rows and the Fig. 7
  "orders of magnitude" claims come from the non-runnable full model.

## Inputs added by the first reader (added.yaml)

- `d0_aortic_root_added`, `d0_mpa_added` and `p_out_zero_added` each have a basis and real alternatives. No
  disagreement.

## Open questions

- Added `q_audit_grid_nodes` (reading, p. 4). The not_runnable_reason of `circulation_1d_0d` says the grid is not
  stated, but p. 4 prints 396 segments, 5359 nodes and 188 junctions. The model still cannot be run.
- The existing questions (`q_mu_av_ratio`, `q_ppc_above_claim`, `q_sip_ratio_reading`, `q_co_lv_rv`,
  `q_svr_definition`, `q_c0_sys_art_min`, `q_mu0_arterial_5`, `q_lvemax_60`, `q_phi_pc_unit`, `q_table2_eq_label`)
  agree with my reading of pp. 6-8 and 11.
