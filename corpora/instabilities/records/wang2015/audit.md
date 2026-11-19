# Audit of wang2015 (second reading, 2026-11-18)

Read pages 1-10 again from the text and checked pages 4-8 against the page images
(Eqs. 3-13, Table 1, the experimental values on pp. 6-7, Methods on p. 8).

## Transcription checks (no changes needed)

- All 22 non-table data in `data.yaml` (pp. 3-8) match the page images: digits, signs,
  exponents and units, including the Methods thicknesses printed in μm (OCR "mm"), the
  ratios 1.59 × 10^3, 9.11 × 10^3, 7.94 × 10^4 (p. 7) and Γ > 10^3 J m^-2, Γ/(μs Hf) > 10^3 (p. 6).
- All 42 Table 1 entries (p. 8) match the page image, including `<10^-3`, `~10^4`,
  `10^-3 - 1`, `10^-3 - 0.2` and `5 × 10^-5 - 5 × 10^-3`.
- Models `eq4_wrinkle_onset` (p. 4), `eq7_crease_wavelength`, `eq8_initial_wrinkle_wavelength`,
  `accordion_eqs9_12`, `eq13_wrinkle_amplitude` (p. 5) match the printed equations: Eq. 4
  coefficients 0.41/-0.59 and 0.50/-0.66 with branch limits 1.3 ≤ μf/μs ≤ 16 and > 16;
  Eq. 8 is 2π(μf/3μs)^(1/3); Eq. 11 carries the factor 2. No corrections.
- Reference attributions checked on p. 9: ref-3 cerda2003, ref-14 richman1975, ref-16 shyer2013,
  ref-43 hong2009, ref-49 cao2012, ref-53 trujillo2008.

## Additions

- `q_eq4_text_slip` (p. 4, possible_error): the sentence before Eq. 4 says "flat and creased
  states" for the boundary set by Π_flat = Π_wrinkle; Eq. 4 is the flat-wrinkle boundary.
- `q_fig5b_10pct_claim` (p. 7, reading): the "within 10%" amplitude claim for Fig. 5B, flagged
  for the figure pass.

## Disagreements and remarks (no change made)

- Printed results still uncompared: `crease_wrinkle_ratio_eq3`, `triple_point_ratio`,
  `crease_to_fold_eM`, `fold_pd_boundary_ratio`, `pd_ridge_boundary_ratio` (pp. 3-5). They are
  outputs of the non-runnable finite element model (`q_fe_not_runnable`), so no run can be
  added; the validator's warnings on them stand. Eqs. 7-13 remain unrun until the figure pass
  (`q_figures_not_read`).
- `cmp_ratio_*` (pp. 7-8): with the Methods moduli the computed ratios are about 0.298,
  134.6, 1538, 9231 and 79808 against the printed 0.3, 130.74, 1.59 × 10^3, 9.11 × 10^3 and
  7.94 × 10^4; the pairing and the precision gap are already in `q_ratio_moduli_pairing`.
- The crease threshold eC_crease = 0.35 (Eq. 3, p. 4) is correctly kept as the energy
  (Maxwell) threshold of ref-43 (stretch 0.65), distinct from Biot's 0.544 (eM = 0.456).
- Eq. 4's upper branch 0.50 (μf/μs)^-0.66 sits close to the classical stiff-film onset
  (1/4)(3 μs/μf)^(2/3) ≈ 0.52 (μf/μs)^-0.667; left for the relation jobs, as the source notes say.
