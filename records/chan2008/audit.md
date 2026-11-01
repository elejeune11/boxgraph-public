# Audit of chan2008

Second, independent reading against the page images, 2026-10-31 (claude-opus-5-5).
The record validated SOUND before the audit (2 warnings: cerruti_force_eq11 and off_rate_eq1 never run).

## Checked, no change

- Table S1 (p. 56): nm_S1 75, Fm_S1 -2 pN, vu_S1 -120 nm/s, nc_S1 75, kon_S1 1 s^-1, koff_S1 0.1 s^-1,
  Fb_S1 -2 pN, kc_S1 5 pN/nm, ksub_range_S1 0.01-100 pN/nm all match the image, including the minus signs
  (they are printed minus signs, not OCR artefacts of "~").
- Fig. S1 legends (p. 33): koff_S1_x3 0.3, koff_S1_div3 0.03, nc_S1B 45, nc_S1C 145 match.
- nu_gel 0.3 (p. 15, below Eq. 8), delta_text 150 ± 30 nm and T_max_text 110 ± 25 pN (p. 24), Delta_fit 277 nm
  (p. 25), T_max_fig -110 ± 25 pN (p. 53, Fig. S10D) match.
- Fig. 3C (p. 4): v_fig3c_260 78 ± 4 nm/s (blue, 260 Pa) and v_fig3c_57k 105 ± 7 nm/s (orange, 57 kPa) match
  the panel; E_260 and E_57k match the caption. q_fig3c_labels (caption swaps stiff/soft) confirmed.
- v_stiff_text ~110 nm/s (p. 6) matches.
- Fig. S12F (p. 55): s12_imposed 80/90/100/110 and s12_measured 83±2, 93±1, 106±2, 114±2 nm/s match.
- Figure readings: v_figS1A_koff01, v_figS1A_koff03, v_figS1A_koff003, v_figS1B_nc45, v_figS1C_nc145 (p. 33)
  agree with my own reading at the decade ticks to within about 2 nm/s; the curve-to-line assignment
  (solid red in S1B = koff 0.03, nc 45; solid green in S1C = koff 0.3, nc 145) is right. v_fig1d (p. 3)
  is plausible within the stated ±5 nm/s at page resolution.
- Models against the printed equations: motor_clutch (Eqs. 1-5, pp. 10-12, and the step order associate ->
  dissociate -> xsub -> vfilament -> displace), off_rate_eq1 (Eq. 1, p. 10), ksub_eq13 (Eq. 13, p. 25),
  cerruti_force_eq11 (Eqs. 11-12, p. 24), motor_clutch_E: symbols, signs and factors as printed; unit
  factors (Pa·nm = 1e-6 pN/nm, Pa·nm² = 1e-6 pN) correct.
- added.yaml: L_eq13_added and E_trace_added each have a basis and real alternatives.
- relations.yaml: rel_bell_off_rate unit factors (1 dyne = 1e7 pN, 1 eV/nm = 160.2 pN) correct.

## Changes

- Added datum delta_fig (p. 53, Fig. S10D in-panel text "<δ> = 150 ± 30 nm, n = 18"), not in the record.
- Added comparison cmp_delta_text_fig (consistency, delta_fig against delta_text, pp. 53 and 24).
- Added question q_U_strain (reading, p. 24): Eqs. 10-12 call U a "strain", but it must be a displacement for
  T to be a force; the record's reading as a displacement is recorded explicitly.

## Disagreements (recorded as questions, not changed)

- q_fig3d_not_compared (reading, p. 4): the first reader left out the Fig. 3D simulation curve. It is the only
  model output the paper ties to Δ = 277 nm, so it is the one printed result that could decide among the
  readings of L_eq13_added (Δ, δ + Δ, δ). I could not read it reliably at page-image resolution either, so
  no datum was added.

No transcription errors were found; no value, model or question was changed or removed.
