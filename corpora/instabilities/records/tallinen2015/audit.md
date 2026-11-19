# Audit of tallinen2015

A second reading of the record against the page images (pp. 1-7). Figures were not read (as instructed).

## Values checked (no change)

- `lambda_s_printed` (p. 2): "≈ 0.647" matches the page. `gs_uniaxial_printed` (p. 2) "≈ 1.55" matches.
- `eta_s_uniaxial_printed` (p. 2) "≈ 1.14", `gb_main_printed` (p. 2) "1.839 . . .", `eta_b_main_printed`
  (p. 2) "0.525 . . . ." match.
- `gb_appendix_printed`, `eta_b_b28_printed` (p. 7) match.
- `gs_equibiaxial_printed` "≈ 1.34" and `eta_s_equibiaxial_printed` "≈ 0.86" (p. 4) match; the same pair is
  printed in Fig. 4(b).
- `eta_4`, `eta_05`, `width_eta4_printed` "7.54", `width_eta1_fe_printed` "4.71" (p. 6) match.
- `fold_spacing_large_g_printed` (p. 2, "about four times") and `eta_brain_printed` (p. 2, "η ≈ 1 [2]") match.
- No transcription error found in `data.yaml`; nothing changed.

## Models checked (no change)

- `eq1_threshold` (p. 2, Eq. 1): all 16 matrix entries agree with the page image, b = 1 + g^4. The common factor
  e^(-ak) on rows 1-2 in model.py only rescales the determinant.
- `eta_b_b28` (p. 2 and p. 7, Eq. B28): numerator and denominator as printed. `eta_b_crossover`: the bracket of
  Eq. B25 as printed; the positive root of its quadratic in eta is B28 exactly (checked by hand).
- `biot_polynomial` (p. 7, g^6 - 3g^4 - g^2 - 1 = 0) and `biot_closed_form` (p. 7) as printed.
- `stiff_threshold_asymptote` 1 + (3/(8 eta))^(2/3) and `stiff_wavelength_asymptote` (8 pi^3 eta/3)^(1/3) match
  the labels of Fig. 1(c) and 1(b) (p. 2).
- `gs_from_stretch` (gs = 1/lambda_s, p. 2), `gs_equibiaxial` (g^(3/2) = gs, p. 4) and `eta_s_equibiaxial`
  (eta -> gy eta, g -> gx sqrt(gy), p. 4) as printed.
- `mode_wavelength_h` uses h = a/gz as printed (p. 1); the variant `mode_wavelength_h_gza` is labelled with its
  correction and evidence. I agree with the first reader's `q_h_relation`: G relaxes the bonded layer, so the
  relaxed thickness is gz a.
- `fe_folding` (pp. 5-6): settings match Appendix A (K = 10^3 mu in 2D, 10^2 mu in 3D, substrate ten times the
  layer thickness, 200 and 10 elements through the layer, widths 2.50h, 4.71h, 7.54h, 30 h domain).

## Questions added

- `q_b27_sign` (p. 7, possible_error): Eq. B27 as printed lacks the minus sign that follows from B26; with A < 0
  at gb the printed form contradicts the sign rule stated after it. No number depends on it.
- `q_fig4_panel_reference` (p. 6, possible_error): Appendix A cites Fig. 4(f) for the large-domain simulation,
  which the caption (p. 4) calls 4(g).
- `q_growth_strain_vs_applied_strain` (p. 5, reading): the growth strain eps = g - 1 is not the equivalent
  compressive strain 1 - 1/g that follows from g = 1/lambda (p. 2); recorded for cross-paper relations.

## Not added (no printed value to compare)

- The intro scaling l ~ h eta^(1/3) (p. 1) has no printed value; its prefactor form is in
  `stiff_wavelength_asymptote`.
- The near-threshold growth values in Fig. 2(c) (g = 1.60, 1.55, 1.28, p. 3) label simulation snapshots. They
  are not results of the record's models.
- Large-eta agreement of Eq. 1 with the stiff-layer asymptotes is shown only in Fig. 1(b),(c); it is left for the
  figure job (`q_figures_not_read`).
