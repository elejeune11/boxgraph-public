# Audit of schwarz2020

Second, independent reading of `corpus/cardio/2020_Schwarz.pdf` (PDF pp. 1-15) against the record,
using the page images. No figure was read and no page was rendered (left to the figure job).

## Values checked against the page images (no change)

- Table 1 (p. 6): all counts, densities, percentages and the five totals (`share_all`, `share_terminal`,
  `share_subepi`, `share_midmyo`, `share_subendo`, `total_*`) match the page, digit for digit.
- `Hd_constant` 0.4 (p. 4), `P_inlet` 90 and `P_capillary` 20 mmHg (p. 5), `d_insilico_max` 400 um (p. 4): match.
- `Gis_prefactor` 1.64 x 10^-3, `Gis_exponent` 2.49 (p. 6): match.
- `Gheart_prefactor` 1.58 x 10^-4, `Gheart_exponent` -2.22 (minus sign confirmed on the image), `Gheart_exponent_internal` 2.18 (p. 7): match.
- `Gheart_exponent_discussion` 2.22 (p. 12, no sign): match.
- `P_fit_prefactor` 5.40 x 10^3, `P_fit_exponent` 0.60, range [250, 800] 10^-6 m (p. 7): match.
- `Q_fit_prefactor` 5.07 x 10^8, `Q_fit_exponent` 2.53; `v_fit_prefactor` 3.00 x 10^4, `v_fit_exponent` 0.89 (p. 7): match.
- `Q_large_median` 36.6 ml/min, `flow_ratio_large_100um` "about 3,000", `wss_small_median` "around 5 Pa", `perfused_volume_total` 358 cm3 (p. 7): match.
- `perfused_volume_median` 20.2 mm3, `perfusion_median` 5.6 ml/min/g (p. 8): match.
- `A_fit_coef_d` -0.66, `A_fit_coef_S` 0.34, `A_fit_intercept` 1.13, `A_median_large` 1.02 (p. 5): match.
- `S_median_large` 0.59 (p. 9), `P_fraction_100um` "around 32%", `gamma_large_close` / `gamma_murray` (p. 11): match.

No transcription error was found in `data.yaml`.

## Models checked against the printed equations (no change)

- `viscosity_eq3` (p. 4): bracket, (d/(d - 1.1))^2 inside and outside, mu*_0.45 = 6e^-0.085d + 3.2 - 2.44e^(-0.06 d^0.645), and C with 10^-11 d^12 all as printed.
- `segment_conductance_eq5` (p. 4): pi d^4/(128 mu l), as printed.
- `wall_shear_stress_eq6` (p. 5): (P_i - P_j) d/(4 l), as printed.
- `area_growth_eq8` (p. 10): A = (1 + S^2)/(1 + S^gamma)^(2/gamma), as printed. The sign of dA/dS stated beside it (f(S,gamma)(S^2 - S^gamma), positive for gamma > 2, S <= 1) is consistent with Eq. 8.
- `area_growth_linear_fit`, the power-law fits and `velocity_fit_from_flow_fit` (8 Q/(pi d^2), d^(gamma-2), unit factors): as printed or correctly derived.
- `area_growth_linear_fit_mm` (variant with dM in mm): a judgement of the first reader, left as it is.

## Additions

- New models: `absolute_viscosity` (Eq. 3's relative viscosity times plasma viscosity, from words, p. 4), `pressure_drop_eq4` (Eq. 4 solved for P_i - P_j, p. 4), `perfusion_from_flow` (the perfusion definition, p. 5).
- New quantities: `plasma_viscosity`, `tissue_density`, `flow_cv`.
- New data: `L_median_all` (Table 1, length median 441 um, p. 6), `CV_flow_text` (7.4%, p. 6), `CV_flow_table2` (0.074, Table 2, p. 10), `perfused_volume_abstract` (20 mm3, abstract, p. 1).
- New added inputs: `plasma_viscosity_added` (1.2 mPa s; alternatives 1.0, 1.35), `d_perfusion_added` (150 um; alternatives 100, 200), `tissue_density_added` (1.05 g/cm3; alternatives 1.0, 1.06). Each has its basis.
- New runs: `run_mu_abs_100um`, `run_G_seg_100um`, `run_dP_100um`, `run_wss_100um` (the flow law at 100 um through Eqs. 3-6, the first runs of Eqs. 5 and 6); `run_Q_perfusion`, `run_perfusion`; `run_Q_1mm`.
- New comparisons for the three printed results that were never compared:
  - `cmp_wss_100um`: against `wss_small_median` ~5 Pa (p. 7). Approximate, so no verdict.
  - `cmp_perfusion`: against `perfusion_median` 5.6 ml/min/g (p. 8).
  - `cmp_Q_large`: flow law at 1 mm against `Q_large_median` 36.6 ml/min (p. 7). The 1 mm value is a lower bound.
- New consistency comparisons: `cmp_cv_flow` (Table 2 p. 10 against the text p. 6) and `cmp_perfused_volume_abstract` (p. 8 against the abstract p. 1).

## Disagreements and new questions

- `q_pressure_fraction_reference` (reading, p. 11): "32% of systemic pressure" may be meant relative to the 90-20 mmHg range rather than to 90 mmHg. The first reader's `systemic_pressure_added` (90; alternative 100) is kept unchanged.
- `q_audit_derived_checks` (choice, pp. 5, 7, 8): the three new approximations evaluate a whole-range fit at one diameter and set it against a class median of the unrunnable network. They depend on the added plasma viscosity, tissue density and representative diameter.
- Note, no change: the large-vessel comparisons combine the median area growth of segments "larger than 400 um" (p. 5; "mother diameter >= 400 um" on p. 9) with the median symmetry for mothers "> 500 um" (p. 9). The comparison notes already say so.

## Validation

`.venv/bin/boxgraph validate corpora/cardio/records/schwarz2020`: SOUND, 0 errors. The 2 remaining warnings say that the unrunnable stochastic models `in_silico_extension` and `network_hemodynamics` are never refined; they cannot be run.
