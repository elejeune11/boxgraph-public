# Audit of bell1978

Second reading of `corpus/1978_Bell.pdf` (PDF pp. 1-10) against the record, by
boxgraph-auditor (claude-opus-5-5), 2026-10-31. Every datum in `data.yaml` was
checked against the page images in `pages/` (digits, sign, exponent, unit, page).
Every model was checked against the printed equation. I could not render the
scan above the resolution of `pages/`, and I could not run `boxgraph build`, so
the computed values below are hand arithmetic.

## Transcription corrections

- `bonds_per_velocity_printed` (p. 7 / 624, Eq. 24): printed `"13"` → `"≈ 13"`. The
  image reads "N_v ≈ 5.3 × 10⁻⁵ v/f_c ≈ 13 v". The OCR renders ≈ as "=" on this page.
  The comparison `cmp_bonds_per_velocity` now gets no verdict. Recorded as `q_eq24_sign`,
  because the image is low resolution.

## Checked and confirmed (no change)

- p. 3 (620): `Ds_B_hapten`, `Ds_A_antibody`, `RAB_075`, `d_plus_s_cgs`, `d_plus_s_molar`
  (printed with "=", not "≈", which is correct), `d_minus_s`, `Kd_s`, `Dm_sum_p3`, `d_plus_m`,
  `d_minus_m`.
- p. 4 (621): every datum, including `kplus_m_cgs`/`kplus_m_um`, `rate_1e5` (≤), `rate_1e3`
  and `rate_1e7`.
- p. 5 (622): every datum, including `E0_antibody_kcal` "8.5" (printed after "="), `tau0_printed`
  "10^-8" and `tau_h_printed` "≈ 5 x 10^-12".
- p. 6 (623): Table 2 matches the image row by row, including the -14.7 entry, which is
  printed as -14.7. `fc_table2`, `force_scale_printed`, `log_coefficient_printed`, `KN2_1e3`,
  `Ks_1e6`, `N2_1e3`, `RAB_1nm`, `fc_eq21_printed` and `fc_representative` also match.
- pp. 7-10 (624-627): every datum matches.
- Models: `encounter_solution` (Eqs. 2-4), `encounter_membrane` (Eqs. 5-6), `max_bond_rate_eq13`,
  `rupture_force_eq15` (1.6 x 10^-5 E0/r0, the paper's own factor), `lifetime_eq16`,
  `detach_time_eq17` (Eq. 17 with Eq. 18 start, γ = r0), `detach_time_eq22_exact`/`_approx`
  (Eq. 22 with Y0 ≈ r0F/kT N1 as printed), `critical_force_eq19_20`, `critical_force_eq21`
  (0.7 ln KN2), `Km_from_Ks` (note 45), `stokes_drag_eq23`, `bonds_to_hold_eq24` and `plug_force`
  all match the printed equations.
- `added.yaml`: `KN2_table2` and `k_minus_table2` have a basis and real alternatives. The
  Fig. 8 caption (p. 7) supports `q_table2_t_method`: "Values of t* were computed numerically,
  but Eq. 22 is a good approximation for f* ≳ 1.0".

## Disagreements and doubts (questions added, nothing changed)

- `harmonic_period` (p. 5 / 622): I also read "τh ≈ 2πr0(E0m)^-1/2" in the image. The model
  implements (E0/m)^-1/2, so it is not the equation as printed. This is the first reader's
  judgement and is left as is, because the printed form is not a time. → `q_tau_h_model_as_printed`.
- `reduction_low`/`reduction_high` (p. 9 / 626): these equal (1 + Kc)^2 to the printed
  precision. That is not stated, so they stay uncompared (the two validator warnings remain).
  → `q_fig5_reduction_reading`.

## Printed results added and compared

- `force_ratio_f0_fc` (p. 6 / 623): fc is "about a factor of 3" below f0. New model
  `force_ratio`, run `run_force_ratio`, comparison `cmp_force_ratio`. The computed value is 3.0.
- `pressure_radius_coefficient` (p. 7 / 624): P = 2γ/R ~ 10^4/R dyne/cm^2 with R in µm. New model
  `laplace_pressure_radius`, comparison `cmp_pressure_radius`. The computed value is 1.0 x 10^4.
- `bonds_pressure_microvillus` (p. 7 / 624): "about two bonds per (0.1 µm)^2". Run of the existing
  `bonds_equivalent_stress`, comparison `cmp_bonds_pressure_microvillus`. The computed value
  is 2.5. The first reader had left this out as feeding no model, but it is a model result.
- `bonds_fiber_cell` (p. 7 / 624), with inputs `bond_density_fiber_max` and `contact_area_fiber`:
  "≤ 3 x 10^5 bonds per cell". New model `bonds_in_contact`, comparison `cmp_bonds_fiber_cell`.
  The computed value is 2 x 10^4 x 16 = 3.2 x 10^5, slightly above the printed "≤" bound
  (no verdict, because of "≤").
- `t_grazing` (p. 8 / 625), with inputs `v_grazing` and `diameter_cell_grazing`: ~10^-4 s. New model
  `travel_time`, comparison `cmp_t_grazing`. The computed value is 1.0 x 10^-4 s.
- `kplus_m_fiber_cgs` (p. 9 / 626): 10^-11 cm^2/sec, restated as 10^-3 µm^2/sec. Consistency
  comparison `cmp_kplus_m_fiber_units`.
- `rate_per_N1_fiber` (p. 9 / 626): dNb/dt ~ 10^-2 N1/msec. New model `max_bond_rate_per_N1`,
  comparison `cmp_rate_per_N1_fiber`. The computed value is 10^-2 per ms.
- `area_duration_N1_1e4` "3" and `area_duration_N1_1e2` "~ 300" µm^2 msec (p. 9 / 626), with input
  `N1_fiber_low`: new model `contact_area_duration`, runs `run_rate_fiber_N1_low`,
  `run_area_duration_N1_1e4` and `run_area_duration_N1_1e2`. The computed values are 3 and 300.
  The model is my reading, not the paper's (it uses the ~300 bonds of p. 625). →
  `q_area_duration_model`.
- New quantities: `force_ratio`, `pressure_times_radius`, `contact_area`, `cell_diameter`,
  `travel_time`, `bond_formation_rate_per_receptor`, `contact_area_duration`.

## Not added

- The plug free energy "60πrh cal/mole per plug" (p. 9). It is a symbolic intermediate, and
  `plug_force` already checks the 120πr step that follows from it.

Validator: `bell1978: SOUND (0 errors, 2 warnings)`. The warnings are `reduction_low` and
`reduction_high`, which belong to the not-runnable Fig. 5 model.
