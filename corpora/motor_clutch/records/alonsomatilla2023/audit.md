# Audit of alonsomatilla2023 (second reading, 2026-11-21)

## Values checked against the page images (no transcription errors found)

- Table 1 (p. 4): `nm_table1` 550, `nc_table1` 470, `Fb_table1` 1.7 pN, `ks_lo_table1` / `ks_hi_table1` 3.5 and 3.5 x 10^4 pN/um: as printed.
- Table 2 (p. 5): `F_table2` 1.38, `tau_table2` 1, `omega_table2` 140, `K_lo_table2` / `K_hi_table2` ~[10^-5 - 10^-1], `Delta_table2` 2.9: as printed.
- SI legends A-E (pp. 19-20): `rho_myo` 3.6 x 10^3, `l_prot` ~1 um, `d_prot` ~50 nm, `nm_si` ~550, `rho_c` 3.1 x 10^3, `nc_si` ~470, `kT_si` 4.114 pN nm, `delta_bell` 2.4 nm, `Fb_si` ~1.7 pN, `d_fa` ~500 nm, `E_lo` / `E_hi` 0.01 / 100 kPa, `ks_lo_si` / `ks_hi_si` 3.5 / 3.5 x 10^4 pN/um (the image shows 10^4, as the first reader recorded): as printed.
- SI Table 2 notes (p. 21): `nm_s2` 550, `Fm_s2` 2 pN, `vu_s2` 240 nm/s, `nc_s2` 470, `kon_s2` / `koff_s2` 1/s, `Fb_s2` 1.7 pN, `kc_s2` 1 pN/nm, `Fth_s2` 5 pN, `T_lo_s2` / `T_hi_s2` 59 / 145 pN, `E_opt_s2` 2.7 kPa: as printed.
- Eq. 6 constants (p. 8): `C2_eq6` 0.4, `C3_eq6` 0.05 (C2 also on p. 27, C3 on p. 29): as printed.
- Figure parameters (pp. 3, 6, 9, 10): `tau_fig1b` 10, `omega_fig1b` 2000, `F1_fig1b`, `F10_fig1b`, `F_fig2f` 2, `tau10_fig2f`, `omega100_fig4`, `omega1000_fig4`, `tau5/20/50_fig4`, `tau10/100_fig5`: as printed.

## Models checked against the printed equations (all match)

- `dimensionless_groups`, `dimensionless_stiffness` (p. 4 text, Table 2); `mean_field` (Eqs. 3-4, p. 4); `kopt_eq6` (Eq. 6, p. 8 = S12, p. 29); `kopt_eq6_dimensionless` (Eq. 6 / nc kc, checked against Fig. S3 at omega = 200 by eye: 0.04 for F = 1, tau = 10); `rigid_steady_state` (S31-S36, p. 33, including the 1/F and 1/F^2 prefactors of beta* and alpha*); `rigid_high_motor` (S55, S57, p. 38); `bell_rupture_force`, `stiffness_from_modulus`, `modulus_from_stiffness` (legends C, E, p. 20).
- `clutch_count` (p. 19): computes rho_c x A where the printed formula divides; the first reader's choice, already in `q_nc_formula`. No change.

## Additions

- Data `C1_eq5` (p. 7, Eq. 5, C1 = 0.4; the SI's OCR reads "C4", the image on p. 31 shows C1) and model `critical_activity_eq5` (Eq. 5 / S20), with `run_eq5_tau10`. Its comparison with the dashed line of Fig. 2(C) is left to the figure job (`q_eq5_vs_fig1b`).
- Model `kopt_s11` (Eq. S11, p. 27, the motor-dominated optimum) with `run_kopt_s11_s2`, and the stated relation `rel_eq6_to_s11` (p. 29: S11 is recovered from S12 when C3 kon nc Fb / koff nm Fm -> 0) in `relations.yaml`.
- The stalled-regime claim T* = F for F = 0.25 and 0.5 "throughout a wide range of substrate stiffnesses" (p. 5, Fig. 1(B)): data `F025_fig1b`, `F05_fig1b`, `T_stall_F025`, `T_stall_F05`; added inputs `K_soft_added` (10^-3) and `K_stiff_added` (1); runs `run_stall_*` of `mean_field` and of `rigid_steady_state` (both roots); comparisons `cmp_stall_*`.
- Quantities `optimum_constant_c1`, `critical_myosin_activity`.

## Findings and disagreements (open questions added)

- `q_stall_bistable` (p. 5, Fig. 1(B)): for F = 0.5, tau = 10, omega = 2000 the record's mean-field solver gives T* = 0.50 at K = 10^-3 but 0.16 at K = 1; S34 has two roots on rigid substrates (T* = 0.50 and 0.16). The paper's line follows the stalled branch.
- `q_mf_initial` (p. 46): the initial condition of the mean-field model is not stated, and it selects the branch where the model is bistable.
- `q_eq5_vs_fig1b` (p. 7): Eq. 5 with C1 = 0.4 gives F_crit = 0.36 at tau = 10, below the F = 0.5 that the paper calls clutch-dominated; by eye the Fig. 2(C) dashed line suggests C1 near 0.3. For the figure job to read.
- `q_caption_c2_c3` (p. 6, p. 28-29): the Fig. 2 caption's t*_rupt has C2 where the SI has C3; SI p. 29 cites "Figure 1F" for Fig. 2(F).
- `q_kcopt_inputs` (p. 9): the inputs of the kappa_c^opt ~ 3.3 pN/nm statement are incomplete; not recorded as a datum (approximate), consistent with the first reader's `q_left_out_models`.
- Reading (no change): Table 1 ranges for Fm, vu, kon, koff, Fth (p. 4) and rho_c ~[500-2500] (p. 19) are not recorded; they feed no printed result.
