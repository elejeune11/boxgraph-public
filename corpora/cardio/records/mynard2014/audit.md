# Audit of mynard2014

Second, independent reading against the page images (2026-11-06).

## Checked, no change needed

- Table 1 (p. 30): all 14 values entered (`bw_*`, `lvfws_*`, `hwbw_*`, `hr_*`, `aobp_mean_*`, `cxq_*`) match the page image: digits, SD and units.
- Table 2 (p. 31): all 84 cells (`t2_*`) match the page image, including the minus signs and `0.0±0.72`.
- Text values match the page images: `p_ra` (p. 6), `scaling_power`, `c_cx` (p. 10), `reff_adult_text`, `reff_newborn_text` (p. 12), `s1_dur_*_text`, `d1_dur_*_text`, `dflow_drop_text` (p. 13), `ws_change` (p. 14), `hw_ratio_text` (p. 18), `hr_ratio_text`, `seglen_ratio_text` (p. 19), and the Fig. 9A labels `fig9a_c_high`, `fig9a_c_mid`, `fig9a_c_low` (p. 41).
- `multiscale_coronary` (pp. 5-8): Eqs. 1-8 in the equation string match the printed forms (signs, factors, exponent b/2, Γ/(A√A) term).
- The processing models (`heart_rate_ratio`, `heart_weight_ratio`, `segment_length_ratio`, `relative_decrease`, `wave_speed_perturbed`, the three difference models) implement what the text states.
- `added.yaml`: `q_lm_adult_added`, `q_lm_newborn_added` (p. 12) have a basis and alternatives (± 1 SD); I agree with them.
- `q_d1_sd` (p. 13), `q_reff` (p. 12), `q_hw_ratio` (p. 18): I agree with the readings.

## Changes

- `effective_resistance` (p. 12): equation string corrected to the printed form with the time-mean bars, `(p̄LM - pRA) / q̄LM` (was `(pLM - pRA) / qLM`). Transcription only; model code unchanged.
- Added printed outputs of the non-runnable multi-scale model as data, so they are recorded and not only listed in `q_multiscale_not_runnable`, with five new quantities (`microvascular_volume_variation`, `normalized_rms_error`, `volume_resistance_share`, `early_systolic_flow_integral_fraction`, `late_systolic_flow_integral_fraction`):
  - `rms_err_adult`, `rms_err_newborn` (p. 13): 16.7 ± 4.9 % and 14.5 ± 4.9 %.
  - `volvar_endo_art_p12`, `volvar_endo_ven_p12`, `volvar_epi_art_p12`, `volvar_epi_ven_p12` (p. 12): 17, 7, 1.6, 2.3 %.
  - `volvar_endo_art_p16`, `volvar_epi_art_p16` (p. 16): 17 and 1.6 %, restated in the Discussion.
  - `rshare_adult`, `rshare_newborn` (p. 12): 40 ± 8 % and 42 ± 8 %.
  - `esfi_lad_adult`, `esfi_septal_adult`, `esfi_lad_newborn`, `esfi_septal_newborn`, `lsfi_lad_newborn`, `lsfi_septal_newborn` (p. 16): 3.2, -1.4, 4.3, -0.7, 7.9, 4.9 %.
  These 12 values (all except the two restated on p. 16) raise the validator warning "never compared with a run". That is expected: only `multiscale_coronary` produces them, and it cannot be run (`q_multiscale_not_runnable`).
- Added consistency comparisons `cmp_volvar_endo_art_text`, `cmp_volvar_epi_art_text` (p. 12 against p. 16).
- Added question `q_feature_point_directions` (pp. 13, 18, 31, `possible_error`): the Results text says the model predicted *smaller* S1a, S1c and D1f in newborns and that both columns show *higher* D1e in newborns, but Table 2 shows the opposite directions; the text also says D1f (experiment) does not differ between groups, while Table 2 flags D1f, not D1e, as different.

## Disagreements with the first reading

- `q_figures_not_read` / `figures.md` (p. 29): the measured Cx flow waveforms of Figs. 7-8 were left unread as "per-animal traces that no runnable model predicts". The guide asks for every plot of measured data to be read; recorded as `q_measured_waveforms_unread` (kind `reading`) for the figure job. Not changed.
