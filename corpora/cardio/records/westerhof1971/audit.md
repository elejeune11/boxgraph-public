# Audit of westerhof1971

A second, independent reading against the page images (pp. 1-6). Table 1 was checked on an enlarged
crop of the existing page image (p. 3). No pages were rendered and no figures were read.

## Values checked, no change needed

- `data.yaml`, all entries (pp. 2-5): digits, signs, exponents and units match the page images. This
  covers the bore (0.45 mm), the viscosity (1.4 x 10^-2 poise; the OCR "10M2" is correctly read as
  10^-2), the density (1.05), Re 1,100, the 1.1 and 0.1 of Eq. 5, the 1.14 x 10^-4 of Eq. 7a,
  Q ≅ 25/f, Q ≅ 8, the 8.5 x 10^-3 of Eq. 11a, the 0.28 of Eq. 11b, the 1.5 x 10^5 of Eq. 8b, 15% and
  +30 degrees at 15 Hz, the pressure drops 180, about 30 and about 50 mm Hg, and the lengths 7.1, 0.92
  and 3.7 cm. Every Table 1 cell (R_c, R_p, C x 10^6, tau, air volumes, minimum lengths, numbers of
  tubes, with their * and † marks) matches. So do the d-c resistances in the captions of Figs. 2-5
  (4,700; 800; 21,300; 3,750).
- `c_*` (p. 3): the row is headed "C‡ x 10^6", with C in g^-1 cm^4 sec^2. Recording the digits in
  cm^4 s^2/Mg (10^-6 cm^4 s^2/g) gives tau = R_p C as printed (for example 1,200 x 800 x 10^-6 = 0.96,
  printed as 1.0). This reading is correct.

## Models checked, no change needed

- `q_eq2` (p. 1, Eq. 2): Q = 6/α², α² = r²ω/ν, ν = μ/ρ. Matches what is printed.
- `rdc_eq1a` (p. 1, Eq. 1a): |Z| = R_c + R_p. Matches.
- `lmin_eq7a` (p. 2, Eqs. 3, 6, 7a): Re = v̄ r/ν and v̄ = ΔP r²/8μl give l > ΔP r³ρ/(8·1100 μ²).
  Matches the printed 1.14·10^-4·ΔP r³ρ/μ².
- `lmin_eq7b` (p. 2, Eq. 7b): the printed l² ≥ (11/64) r·ΔP r³ρ/μ² is the same as the model's
  a/(64 ε) r⁴ρΔP/μ² with a = 1.1 and ε = 0.1. Matches.
- `k_eq8b`, `tubes_eq8b` (pp. 2-3, Eq. 8b): R = 8μl/(πr⁴N), and R ≅ 1.5·10^5 l/N. Matches.
- `air_volume_eq9` (pp. 2-3, Eq. 9): C = V/P, with P the absolute pressure (atmospheric plus mean
  arterial, p. 3). Matches.
- `impedance_eq10` (p. 2, words): Q = R/ωL = 1/tan φ. Correctly entered as `from_words`.
- `lmin_eq11b` (p. 3, Eq. 11b) and `tau_rpc` (p. 5, exp(-t/R_pC)): match.

## Changes made

- `cmp_lmin_rp_pulm_text_tab` (p. 3): **added** a `consistency` comparison of the two printed
  minimum lengths of the pulmonary R_p: 0.92 cm in the text and 1.3 cm in Table 1. Before this, each
  was compared only with Eq. 11b, never with the other.
- `q_implied_bore` (p. 3): **added** a question of kind `unexplained_difference`. The Eq. 11a, Eq. 11b and
  Eq. 8b constants each imply a bore of about 0.44 mm (r ≈ 0.219-0.221 mm). Q ≅ 25/f instead fits the
  printed 0.45 mm. This links the first reader's `q_eq11_coefficients` and `q_eq8b_constant`.
- `q_eq7b_coefficient_not_compared` (p. 2): **added** a question of kind `reading`. Eq. 7b's constant
  is printed as the fraction 11/64. The printed-value grammar cannot read a fraction, so the constant
  is not a datum. The model builds it from Eq. 5's 1.1 and 0.1.

## Unstated inputs (`added.yaml`), no change

- `p_atm_added` (760 mm Hg; alternatives 750, 770) and `pmean_pulm_added` (15 mm Hg; alternatives 30,
  40): each has a basis and real alternatives. Question `q_air_volume_pressure` records that
  the pulmonary choice could change verdicts. I agree with both.

## Disagreements and remarks (no change; judgement of the first reader)

- `lmin_rc_pulm_tab` (p. 3): this is still the validator's one warning. No pressure drop over the
  pulmonary R_c is printed, so no run is possible. Question `q_lmin_pulm_rc` covers it. I leave it.
- Left out on purpose by the first reader, and I agree: "only about 20 mm Hg" over R_c, "50% of
  200 mm Hg", "0.5 x 100 = 50 mm Hg", the 25 mm Hg for the second harmonic (p. 4), "about 180 mm Hg"
  over R_p, "R_c is about 25% of R_p" (p. 3), and "10% error in bore gives about 40% in R" (p. 3).
  All are printed as approximate ("about"), so none could get a verdict. The 40% is consistent with
  R ∝ r^-4 (an error between 34% and 52%).
- `source.yaml` `reader.model` is `None`. This is metadata, not a value from the paper, so I left it.
- Figs. 2-5 (pp. 3-5) carry measured impedance data and, in Figs. 4-5, the theoretical curve from
  Table 1. They are not read yet; that is the next job (see `q_figures_not_read`).

Validator after the audit: SOUND (0 errors, 1 warning: `lmin_rc_pulm_tab` not compared).
