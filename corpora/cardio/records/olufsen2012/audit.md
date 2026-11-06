# Audit of olufsen2012

Second, independent reading against the page images. Figures were not read; that is the next job's work.

## Values checked, no change needed

- k1_systemic, k2_systemic, k3_systemic (p. 6): 1.50 × 10^4 mmHg, −25.5 cm^-1, 349 mmHg match the page, including the exponent and sign.
- epsilon_pulmonary (p. 7): ε ≈ 0.02 mmHg^-1 matches. Eh_r0_pulmonary (p. 7): 34.5 mmHg matches the page. The 37.5 mismatch is already q_Eh_r0_pulmonary.
- xi_base, eta_base, gamma_base, rmin_systemic, rmin_pulmonary (p. 9): 2.76, 1.16, 0.41, 100 µm and 50 µm match.
- lrr_systemic (p. 10): 50 matches.
- fig5_* (p. 10): the labels on Fig. 5 read 1.103 / 2.5193 and 0.04733 / 0.6309, as recorded.
- eq219_* (p. 10): e^2.52, exponent 1.10 and 12.4 match.
- table2_* (p. 21): all 18 entries match the page image.
- FA_pulse_plateau (p. 19): "around 33 mmHg" matches the page image; it is not an OCR error.
- eq41_*, eq42_* (pp. 23-24): 1.50, 0.46, 0.71, −0.66, 0.79 and 1.12 match.

## Models checked, no change needed

- stiffness_eq28 (p. 7): Eh/r0 = 3/(4ε), as printed.
- area_ratio_eq218 (p. 9): the right-hand form (1+γ)/(1+γ^(ξ/2))^(2/ξ), as printed.
- area_ratio_eq216_217 (p. 9): the left-hand form with γ = r_d1/r_d2, reduced correctly to (1+γ²)/(1+γ^ξ)^(2/ξ).
- prefactor_eq219 (p. 10), pulse_coefficients_eq42 and pulse_pressure_eq42 (pp. 23-24): as printed.

## Changes made

- Added data eq31_sys_slope, eq31_sys_intercept, eq31_pulm_slope and eq31_pulm_intercept (p. 15, Eq. 3.1: p_sys = 60 log10 r_sys − 110, p_pulm = 14 log10 r_pulm − 25). Added two quantities to go with them: pressure_log_radius_slope and pressure_log_radius_intercept. These are printed results fitted to the simulated curves of Fig. 7(d), and the first reading left them out. They stay uncompared until Fig. 7(d) is read.
- Added question q_table2_trend_claims (overstated_claim; pp. 18 and 21). The paper says the rise in mean pressure is "almost linear" and that pulmonary pulse pressure "goes down" with rarefaction. The PuA rows of Table 2 (means 5, 10, 33; pulse pressures 12, 12, 3) do not fully bear that out.

## Disagreements (recorded, not changed)

- q_eq31_scope (reading; p. 15): source.yaml's notes list Eq. 3.1 as out of scope. I think its coefficients belong in the record, so I added them as data (above). The first reader's scope note is left as it is.
- source.yaml (no page): `reader.model` is the string "None". This is the first reader's metadata, so I have not changed it.
- The Levy et al. estimate p = 50 log10 r − 5 (p. 15) is still left out. It is the authors' estimate from another paper's figure, not a result of this paper's models.
