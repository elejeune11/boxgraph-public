# Audit of prahl2020

Second reading of `corpus/motor_clutch/2020_Prahl.pdf` against the record, from page images (figures not read).

## Checked, no change

- Table S1 (p. 22): all 20 values in `data.yaml` (nmotor ... psi_pol) match the page in digits, exponent and unit, including koff 10^-1 s^-1, kcap 10^-3 s^-1, ksub 10^3 pN/nm, kcell 10^4 pN/nm and Lmin 100 nm; the 0.1 and 10 constraints in the Source column are as printed.
- `ksub_text` (p. 4): 1000 pN nm^-1 as printed.
- `fold_10`, `nclutch_75` (p. 7): as printed.
- `v_exp`, `v_exp_nm_s`, `mu_exp`, `mu_sim`, `v_sim` (p. 6, text and Fig. 3 legend): as printed.
- `v_sim_approx`, `tumor_rate_printed` (p. 9): as printed ("~0.5 um per min^-1", "25 cm per year^-1").
- `S_prw`, `S_prw_nm_s`, `logP_mean`, `P_1258`, `t_imaging_h`, `t_imaging_min`, `log_t_imaging` (p. 27, Fig. S4 legend): as printed.
- `w_channel`, `h_channel`, `A_channel`, `b_square`, `L_channel`, `mu_water`, `dg_printed`, `v_cell_drag`, `Fdrag_printed` (p. 21): as printed; `v_cell_drag` is printed in um s^-1 on the page (already a question, q_drag_velocity_units).
- Models `slip_bond_s1` (Eqn. S1, p. 14), `force_velocity_s2` (Eqn. S2, p. 14), `polymerization_s3` (Eqn. S3, p. 15), `nucleation_s8` (Eqn. S8, p. 15), `drag_coefficient_s9` (Eqn. S9, p. 20), `drag_force_s10` (Eqn. S10, p. 21), `msd_prw_eq1` (Eq. 1, p. 6), `msd_drift_eq2` (Eq. 2, p. 6): equal to the printed equations in symbols, signs and factors; the unit bookkeeping in `drag_coefficient_s9` is right (12 x 10^-3 Pa s x 1 mm / (7.5 um)^2 = 0.213 pN s um^-3).
- `cms_1d` (pp. 14-16): its summary of Eqns. S1-S8 and the analysis settings (5 min sampling, first hour dropped, >1 um/s filter, first half of the MSD) match p. 16.
- `added.yaml` is empty: no model with a run needs an input the paper does not print (the MSD fit models have no runs, and their n is a question, q_msd_n). No change.
- Carry-over to the 2D CMS: q_params_vs_2d checked value by value against bangasser2017/data.yaml (Supplementary Table 2); it holds.
- "~4 myosin motors" (p. 21): 6.5 pN / 2 pN = 3.3 motors; approximate, not entered.

## Changes

- Added datum `Fdrag_main` (p. 10, Discussion): the main text's "~6.5 pN" drag force, printed separately from Eqn. S10's -6.5 pN and not recorded before.
- Added comparison `cmp_fdrag_main` (consistency, Eqn. S10 result against `Fdrag_main`; approximate, no verdict).
- Added question `q_glass_modulus` (possible_error; pp. 10 and 20): glass modulus printed as ~10^7 kPa in the Discussion and ~10^6 kPa in the Supplemental Notes.
- Added question `q_clutch_timescale` (overstated_claim; pp. 9 and 20): the stated ~10^-1-10^-3 s ("milliseconds") clutch timescale is shorter than 1/kon = 1 s and 1/koff = 10 s of Table S1.
- Added question `q_eqn_s6_index` (possible_error; p. 15): Eqn. S6 sums the cell-body clutches to nclutch,j instead of nclutch,cell.

## Disagreements with the first reading (recorded as questions, nothing changed)

- `q_params_vs_2d_now_checkable` (reading; p. 22): the source notes and `q_params_vs_2d` say bangasser2017's record has no data; it now does, and the values agree. The 2D and 1D initial conditions differ (three equal modules against two +x and one -x, p. 16). The notes were left as written.
- Source notes (p. 10 and p. 20): the notes give the glass modulus as 10^7 kPa only; the Supplemental Notes print 10^6 kPa. Recorded in q_glass_modulus; notes not edited.
