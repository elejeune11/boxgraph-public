# Audit of boileau2015

A second, independent reading of `corpus/cardio/2015_Boileau.pdf`, checked against the page images. Figures were not read here.

## Checked, no change needed

- **All values in `data.yaml`** match the page images: digits, signs, powers of ten, units and pages.
  - Table II (p. 7): `h_sp`, `rho_sp`, `mu_sp`, `zeta_sp`, `E_sp`, `L_sp`, `c0_sp`.
  - Eq. 14 and its text (p. 15): `q_amp_eq14`, `k_eq14`, `t0_eq14`, `q_peak_sp`, `width_sp`, `wavelength_sp`, `c0_sp_text`.
  - Table III (p. 9), all entries, including R1 2.4875·10^8, C 1.7529·10^-10 and R2 1.8697·10^9.
  - Table V (p. 11), all entries.
  - Table VII (p. 13), both columns.
  - p. 27: `wavelength_car`, `wavelength_ao`.
  - Table XI (p. 17): `rho_adan`, `E_adan`.
  - Eq. 17 (p. 21): `a_eq17`, `b_eq17`, `c_eq17`, `d_eq17`. The minus signs of b and d are on the page.
  - Table XII (p. 23) and Table XIII (p. 24): all 31 terminal distal radii and R1 values (`R1_adan_xii`, `R1_adan_xiii`), entry by entry.
- **The circumflex in "9.46̂ kPa"** (pp. 11, 13) is on the page, as the record's note says.
- **Models against the printed equations.** No change needed:
  - `pwv_eq5_reference` and `pwv_at_pressure` match Eq. 3 and Eq. 5 (pp. 3–4).
  - `windkessel_mean_pressure` matches Eq. 9 (p. 5), averaged over a period.
  - `gaussian_inflow_eq14` matches Eq. 14 (p. 15).
  - `peak_decay_eq15` matches Eq. 15 (p. 15).
  - `initial_area_eq16` matches Eq. 16 (p. 15).
  - `adan56_terminal_impedance` matches Eq. 17 (p. 21).
  - The symbols, signs and factors (4/3 √π E h, (ζ+2)πμx/(ρ c0 A0)) are as printed.
- **ADAN56 R1 ratio** (`q_adan56_r1`, pp. 23–24): spot-checked R1/(R1+R2) = 0.2, for example 18104/(18104+72417).
- **Table IV** (p. 11): the E^RMS_Δr row is 0.96, 1.00, 1.00, 1.07, 1.01, 0.98, as `q_overstated_carotid` says.
- **No transcription errors were found**, so no existing datum, model or question was changed.

## Added by the audit

- **Table I CFL numbers, single pulse** (p. 6). These are printed results of a formula the paper states (footnote: CFL = λΔt/Ωe, λ = max|U+c|), and they were not compared.
  - Data: `dt_sp_{dcg,lcg,fvm,mcc}`, `dx_sp_*` and `cfl_sp_*`.
  - Model: `cfl_table1`.
  - Runs: `run_cfl_sp_*`. Comparisons: `cmp_cfl_sp_*`.
  - Quantities: `time_step`, `element_size`, `cfl_number` and `flow_velocity`.
  - LCG, FVM and McC reproduce (0.031, 0.90, 0.99).
  - DCG gives 0.031 against the printed 0.18 (see `q_cfl_dcg_sp`).
  - FEM and STM are printed as NA.
- **Added input `U_max_sp`** (p. 15, Table II): the largest single-pulse velocity, Q_peak/A0 = 0.0032 m/s, with 0 as the alternative. λ = c0 + U for the single pulse.
- **Datum `wavelength_sp_p24`** (p. 24): the second printing of the single-pulse wavelength "≈ 31 cm vs 10 m". It is compared with `wavelength_sp_pred` in `cmp_wavelength_sp_p24`. The value is approximate, so the comparison gets no verdict.
- **Question `q_cfl_dcg_sp`** (p. 6, `unexplained_difference`): the DCG single-pulse CFL does not follow from the printed formula.
- **Question `q_cfl_other_cases`** (p. 6, `choice`):
  - The other cases' CFL numbers need max|U+c| from solver output, so they are not checked.
  - A rough back-calculation of λ for carotid FVM and aorta McC gives less than the printed cm.
- **`source.yaml` notes:** I added one sentence pointing to this audit. The first reader's text is unchanged.
- **Question `q_eq16_wording`** (p. 17, `possible_error`): the text derives Eq. 16 by "considering P = 0, A = Ad". It should be A = A0; the equation itself is consistent.

## Disagreements with the first reading (not changed)

- **The `n_one` and `n_two` warnings:** these added outlet counts have no alternatives. They are structural, not values, so I left them as the first reader set them and raised no question.
- **Scope note in `source.yaml` ("Table I … is not recorded")** is now partly outdated: the single-pulse CFL rows are recorded. The rest of Table I is still left out.
