# Audit of cerda2003

A second reading of PDF pp. 1-4 against the record, from the page images.

## Values (data.yaml)

- No transcription errors found. Every value was checked against the page image: `L_fig1` (≈ 25 cm),
  `W_fig1` (≈ 10 cm), `t_fig1` (≈ 0.01 cm), `gamma_fig1` (≈ 0.10) on p. 1; `E_over_Es_apple` (~ 10),
  `lam_over_t_apple` (~ 3), `t_apple` (≈ 0.5 mm), `lam_apple` (≈ 1.5 mm), `E_over_Es_skin` (~ 10^3),
  `Hs_over_t_skin` (~ 10), `lam_over_Hs_skin` (≈ 1), `two_Hs_hand` (≈ 5 mm), `lam_hand` (≈ 2.5 mm),
  `B_vesicle` (≈ 4.6 x 10^-17 N m, exponent -17 confirmed) on p. 3; `t_vesicle` (43 nm) on p. 4.
- Added `gamma_text_fig1` (p. 1): "For the sheet shown in Fig. 1, gamma ≈ 10^-2", a printed value the first
  reading left out. No comparison added; see the disagreement below.

## Models

- No equation errors found. Checked against the page images: `bending_stiffness` (p. 2),
  `energy_minimum` (U, p. 2), `wrinkle_eq5` (Eq. 5, p. 2), `stretched_sheet` (p. 2; both forms, and both
  follow exactly from Eq. 5 with T = E t gamma, Delta = nu gamma W), `wrinkle_eq6_scaling` (Eq. 6, p. 2),
  `persistence_length` (L_d ~ lambda_d^2 gamma^(1/2)/t, p. 2), `deep_substrate_wavelength` and
  `shallow_substrate_wavelength` (p. 3), `bending_from_wavelength` (B = T lambda^4/16 pi^2 L^2, p. 3),
  `membrane_thickness` (from words, p. 4).
- Added model `amplitude_inextensibility` (p. 2): the stated constraint A_n^2 k_n^2 W/8 ≈ Delta, which is
  how Eq. 5's amplitude is obtained "using (2)".
- Added relation `rel_eq5_amplitude_same_as_inextensibility` (p. 2): Eq. 5's A against that constraint at
  Eq. 5's wavelength (stated: "obtained by minimizing U and using (2)").

## Comparisons

- The four existing comparisons (`cmp_apple_ratio`, `cmp_apple_wavelength`, `cmp_skin_ratio`,
  `cmp_hand_wavelength`, p. 3) cover every numerical result the paper derives from its models with
  printed inputs. The vesicle results (`B_vesicle`, `t_vesicle`) cannot be run: their inputs are not
  printed (agree with `q_vesicle_inputs`, `q_vesicle_thickness`). The prefactor-1 value 10^(1/3) ≈ 2.2
  against the printed "3t" (`q_apple_factor`) was rechecked and is right.

## Unstated inputs

- `nu_polyethylene_added` has a basis and real alternatives (0.3 to 0.5); it feeds no compared result.
  No other unstated input found.

## Disagreements and new questions

- `q_audit_gamma_two_values` (p. 1, reading): the text's gamma ≈ 10^-2 is written with the symbol of the
  applied strain; the first reading takes it as gamma_c. Left to the first reading; recorded.
- `q_audit_substrate_derivations` (p. 3, reading): the deep/shallow laws' derivation from Eq. 6 with
  K depending on lambda is not tested by any relation (implicit in lambda).
- `q_audit_untested_scalings` (pp. 2-3, reading): "L_d ~ L" and "T ~ B L^2/lambda^4" are stated but not
  tested or entered.
