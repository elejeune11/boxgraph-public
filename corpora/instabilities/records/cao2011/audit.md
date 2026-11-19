# Audit of cao2011

A second, independent reading against the page images (2026-11-19). Figures were not rendered or read.

## Checked, no change

- `lambda3_plane_strain`, `r_printed`, `ratio_W_printed`, `coef_W_printed`, `ratio_C_hong`, `coef_C_printed`
  (pp. 2, 5, 15): digits match the page images (1, 3.3830, 0.2956, 0.5437, 0.42, 0.65).
- `eps_W_printed` (p. 16, Fig. 5 caption; also p. 17 and Fig. 9 label p. 19) and `eps_C_printed` (p. 17): 0.456 and 0.35 match.
- `A_printed`, `b112_printed` ... `b156_printed` (p. 9, Eqs. 4.2-4.3): all six b_ijm and A match the image.
- `K_imperfection_printed`, `c_printed` (p. 10, Eq. 4.4): 17.8405 and 0.95467 match.
- `energy_two_mode_printed` (p. 11): -0.651 matches.
- `cstar_two_mode_printed` (p. 13, Eq. 4.9): 1.7534 matches. The OCR loses the square roots; the image shows
  lambda* - lambda_W = lambda_W sqrt(3 sqrt(3) b112 c |xibar_1| / 4) = 1.7534 lambda_W sqrt(|xibar_1|), which
  is what `two_mode_cstar_eq49` codes.
- `cstar_table1_max_strain`, `cstar_table1_local_strain` (p. 14, Table 1): all ten entries match.
- `cstar_shape_printed` (p. 14, Eq. 4.10): 1.9541 = 2 sqrt(c) matches, and the model matches the printed form.
- Models `biot_eq28` (Eq. 2.8, p. 5), `crease_eq12` (Eq. 1.2, p. 2), `quadratic_coefficient_eq38` and
  `cubic_coefficients_eq37` (Eqs. 3.7-3.8, p. 8, with the modes of Eqs. 2.9-2.10, p. 5), `imperfection_energy_eq313`
  (Eq. 3.13, p. 9: the image does print `-mu lambda_1 l (r - 1)^2`), `c_definition_eq44` (p. 10), `two_mode_energy`
  (Eqs. 4.7-4.8, p. 10): each matches the equation as printed. The variant `imperfection_energy_eq313_r2m1` stays a
  variant beside the printed form, with its evidence, and `q_eq313_prefactor` stays open.
- `source.yaml` (p. 1): title, authors, venue, DOI and the page labels 94-115 match.
- Scope: the paper has no film/substrate formula and no prestretch (searched every page; p. 114 mentions
  film/substrate systems only qualitatively). So wang2014's Eq. 5 and its 2^(2/3) factor cannot be checked against this
  paper; that is the companion cao2012. Strain here is nominal, eps = 1 - lambda along x1 with lambda_3 fixed, as the
  notes say.

## Added

- Printed results not compared yet (p. 9, Eq. 4.3): the paper prints `b112 = b224/4 = b336/9 = 2.4792` and
  `b123 = b246/4 = 9.6303`. The first reader used these relations inside the N-mode model but did not compare them.
  Added quantities `coupling_b224_quarter`, `coupling_b336_ninth`, `coupling_b246_quarter`, data
  `b224_quarter_printed`, `b336_ninth_printed`, `b246_quarter_printed` (p. 9), model
  `cubic_coefficient_relations_eq43` (Eq. 3.7 evaluated for the triples (2,2,4), (3,3,6), (2,4,6), with the same
  integrand as `cubic_coefficients_eq37`), run `run_b_relations` and comparisons `cmp_b224_quarter`,
  `cmp_b336_ninth`, `cmp_b246_quarter`. All three reproduce: 2.47919, 2.47919, 9.63034.
- `source.yaml` notes: the sentence that listed these relations as left out now says the audit checks them.

## Disagreements

- None that changes a datum or model. Two remarks, not recorded as questions:
  - p. 14, "underestimates ... by about 35 per cent": 2.358/1.754 = 1.344, so the 35 per cent is measured against the
    two-mode value (against the six-mode value it is 26 per cent). The record leaves it out as approximate, which I keep.
  - p. 17, "imperfections larger than about xibar_1 = 0.008" (finite elements): the six-mode asymptotic row (i)
    gives eps* = eps_C at xibar_1 ≈ 0.0069 in plane strain. The two are consistent at the "about" level. No verdict is
    possible, so I added no question.
- No transcription errors were found, so no value or equation was corrected.

Validator: `cao2011: SOUND (0 errors, 0 warnings)`.
