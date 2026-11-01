# Audit of gong2018

Second, independent reading against the page images (claude-opus-5-5, 2026-11-01).

## Checked, no change

- Table S1 values (p. 20): nm_tableS1, Fm_tableS1, Fcr_tableS1, nc_tableS1, Fb_tableS1, ron0_tableS1,
  roff0_tableS1, kc_tableS1, vu_tableS1, Vp_tableS1, alpha_tableS1: digits, units and exponents match
  the page image.
- Fb_meanfield (p. 11, 1.3 pN): matches.
- ka_fig1, kl_fig1, eta_fig1 (p. 3, Fig. 1 caption): match. ka1/eta1/kl/ka2 of Fig. S8D (p. 19): match.
- kl_fig2b, ka01/ka05/ka2_fig2b (p. 4, Fig. 2 caption and legend): match.
- R_contact, nu_S9, coef_S9 (p. 12), E_1kPa, k_1pNnm (p. 4), tau_b_printed (p. 7): match.
- vs_PA_effective, vs_PA_multiple, vs_HA_effective, vs_HA_multiple, increase_PA_printed (p. 13): match
  the page image (97.2, 101.1, 74.6, 75.4 nm/s; 4%).
- mean_field_sls (pp. 2, 11): Eqs. S3, S5, S6, S8, Eq. 6, <roff> = roff0 exp(Fc/Fb) and the
  reinforcement rule are coded as printed. The code writes Eq. S4 as a spring kl in parallel with a
  Maxwell element (ka, eta); I checked algebraically that this is identical to Eq. S4 / Eq. 2 as printed.
- mean_field_maxwell2 (p. 12, Eqs. S11-S12): as printed; eta2 = ka2 tau_s2 from tau_s,i = eta_i/ka,i (p. 13).
- mean_field_elastic: mean_field_sls with no Maxwell element; consistent with "purely elastic" (p. 3).
- boussinesq_eq_s9 (p. 12): 4/7 pi R E / ((1 + nu)(1 - 0.86 nu)) as printed; the unit conversion
  um * kPa = pN/nm is right.
- lifetime_timescale (pp. 5, 12), binding_timescale (p. 5), relative_increase (p. 13): as printed.
- Added inputs alpha_none, kl_range_low, kl_range_high: have a basis and alternatives.

## Changes

- Added datum `r_printed` (p. 12, "r = 2R = 1 μm"), model `fa_length` (r = 2R), run `run_fa_length`
  and comparison `cmp_fa_length`: a printed intermediate result not compared before. New quantity
  `fa_characteristic_length`.
- Added datum `Vp_figS2` (p. 15, Fig. S2 caption, Vp = 40 nm/s): a printed parameter that differs from
  Table S1; recorded with question `q_vp_two_values` (p. 15 / p. 13).
- No transcription error found; nothing in data.yaml or the models was changed.

## Disagreements and new questions

- `q_audit_unread_results` (reading; pp. 3, 5, 16): Fig. 3A, the dash-dotted averages of Fig. 3C and
  Fig. 1D, and Fig. S3D are model results at printed parameters that the record does not compare;
  run_fig1_params produces Vs, t_life, Fa that are compared with nothing. Figure rendering
  (`boxgraph figure page/check`, `pdftoppm`) was not permitted in the audit session, so no readings
  were added and the existing figure readings were not re-run with overlays; the first reader's
  overlay crops in figwork/ (fig1b_red_ov.png, fig2b_g_ov.png) were looked at and show the intended
  series.
- `q_eq_s9_symbol` (possible_error; p. 12): Eq. S9 reuses kc, the clutch-stiffness symbol, for the
  substrate spring constant.
- `q_vp_two_values` (unexplained_difference; pp. 13, 15): Vp = 40 nm/s in Fig. S2 vs 120 nm/s in
  Table S1, though the SI says the other parameters are kept constant for all simulations.
- Not added (out of the record's scope, noted only): "the simulated maximum force is around 30 pN"
  (p. 13) is a KMC result for a single clutch; the KMC model is not in the record.
- tau_l range (q_tau_l_range, p. 8): I agree with the first reader. Note for a later reader: with
  Table S1 values tau_l = Fm Nm/(vu kl) over kl = 10^-2 to 10^2 pN/nm spans one decade lower than the
  printed 10^-1 s to 10^3 s (the runs run_tau_l_low / run_tau_l_high show this).
