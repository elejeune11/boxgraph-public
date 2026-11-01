# Audit of bangasser2013b

Second, independent reading against the page images (pp. 2-9, 12-20).

## Checked, no change

- Table S1 (p. 18): nm_base, Fm_base, vu_base, nc_base, kon_base, koff_base, Fb_base and kc_base are as printed, including the printed unit 'pN/nm' of vu (see below).
- Figure conditions: ks_fig2 (p. 6), r_fig2 (p. 5), r_fig4 and n_fig4_* (p. 7), r_S2E_* (p. 14), eps_choice (p. 5), nm_S1/nc_S1 (p. 12), ks_S1 (p. 16) and r_S2F_2 (p. 17) are as printed.
- Fig. 4 optima ksopt_mc_n25/n3600 (0.4, 50) and ksopt_ode_n25/n3600 (1, 200) (p. 7) are as printed.
- tcycle_r1_text/tcycle_r3_text (15 s, 73 s) (p. 14) are as printed.
- The Discussion values Fm_order, vu_order, Fm_vu_text, nfac_text, L_text, L_fold_text, Fm_vu_subst, nfac_subst, L_subst, coef_eq31, kon_koff_ratio, kon_range_text and koff_range_text (p. 9) are as printed.
- The eye readings tfail_fig2b_ode, xs/Fc/vf/Pb_fig2* (p. 6), the Fig. S1 plateaus (p. 19) and tcycle_figS2f_r2 (p. 20) agree with my own look at the images. They stay approximate (q_eye_readings).
- Models single_clutch_ode (Eqs. 1, 2, 4-7, p. 2-3), clutch_ensemble_cycle/_timecourse/_optimum (Eqs. 8-12 and 19, pp. 3-4), optimum_eq30 (Eq. 30, p. 5), eq31_factors/eq31_coefficient/eq31_rates (Eq. 31, pp. 8-9) and log_cycle_factor (p. 9) implement the equations as printed: signs, the exponent -r of Eq. 19, and the reduction of Eq. 12 with Eq. 10.

## Changes

- **n_order** (p. 9): printed was "1000"; the page says 'of order 1000'. Corrected to "~1000", as Fm_order and nfac_text already do for 'on the order of'.
- **traction_order** (p. 9, new datum, quantity traction_force): 'traction force on the order of 1000 pN' (refs. 4, 28), printed "~1000".
- **motors_for_traction** (p. 9, new model, from words): n = F/Fm. New run **run_motors_for_traction** and comparison **cmp_n_traction** against n_order. This is the step the paper uses to get n ≈ 1000, which no comparison covered. Both sides are approximate, so the comparison gets no verdict.

## New open questions

- **q_audit_ode_vs_mc_slightly** (overstated_claim, pp. 5, 7): the paper calls the ODE optimum 'slightly' higher than the Monte Carlo one, but its own printed optima differ by factors of 2.5 and 4.
- **q_audit_fig2b_vs_S2E** (unexplained_difference, pp. 6, 20): by eye, the r = 2 ODE failure is near 28 s in Fig. 2B but near 31-32 s in Fig. S2E. These would agree if S2E is on the base set at 0.1 pN/nm.

## Disagreements with the first reading (not changed, recorded as `reading` questions)

- **vu_base** (p. 18), **q_audit_vu_unit_reading**: the unit nm/s is an interpretation of the printed 'pN/nm', so strictly it is an assumption that could sit in added.yaml. The first reader's handling (note + q_vu_unit) is kept.
- **t_S1_late** (p. 19), **q_audit_t_S1_late**: 20 s is the reader's choice of evaluation time, not a stated input. It could sit in added.yaml. It has no effect on the plateau values.

## Not added

- Fig. 6 run times (p. 8) and the Monte Carlo statements of pp. 12-15 (S1A cycle ~5 s, minimum r ≈ 2): these come from the software or from the Monte Carlo model, not from this record's models. This agrees with the first reader's scope.
- Euler's constant γ ≈ 0.577 (Eq. 21, p. 4): a mathematical constant, left out as the first reader decided.
