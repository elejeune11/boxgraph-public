# Audit of savin2011

A second reading against the page images (2026-11-19). The page images are about 110 dpi, so the tables and
footnotes were checked on magnified crops of `pages/page-NNN.png`; no page was rendered and no figure read.

## Checked, no change

- **Table 1 (p. 4)**: every n, lambda and R of the six rows (E8, E12, E16; observation and "Computational
  model") and every footnote input (Lt, h, ro, ri, Em, Et, eps_p, eps0 for E8, E12, E16) matches `data.yaml`:
  digits, ± values, units (mm, um, kPa, %).
- **Table 2 (p. 5)**: the same for quail E12, finch E13 and mouse E16.5; all match.
- **Eqs. 1, 2 (p. 3)**: printed with ∝, so `prefactor: unknown` in `wavelength_eq1` and `radius_eq2` is right;
  It ∝ ro^4 - ri^4 as entered.
- **Eqs. 3, 4 (p. 4)**: lambda ≈ 36 (Et It/(Em h))^(1/3) and R ≈ 4 (Et It/(Em h eps0^2))^(1/3); `wavelength_eq3`
  and `radius_eq4` match. It = (pi/4)(ro^4 - ri^4) checked in SI footnote 6 (p. 16). Hand check: chick E8 gives
  6.05 mm against the printed 6.1.
- **SI p. 6 (page 13)**: dF/d delta ≈ 10^-4 N, dF/d eps ≈ 10^-3 N, v0 ≈ 1.5 ro, ri = 230 um, ro = 390 um,
  Et It = 5 x 10^-11 N m^2, F = (Et It/v0^2) delta and 4 Et It/(ro^2 + ri^2); all match the two stiffness models.
- **SI p. 8 (page 15)**: 0.36, 2a1, k1 a1^2 = 5.6 b1, kt ro^2 = 4/(1 + (ri/ro)^2) bt, 0.3 < ri/ro < 0.6,
  2.9 bt < kt ro^2 < 3.6 bt, footnotes 3 and 4; all match.
- **Methods (p. 7)**: bead radii, 2 mm < d < 8 mm, "1 μN to 1 mN" (the OCR's "1 mN to 1 mN" is correctly noted
  on `F_range_low`); Fm and Ft of `lattice_simulation` match the printed energies.
- **Table S1 (p. 10)**: the three F0 (2.40, 3.07, 1.05 with exponents -3, -2, -1) and alpha (3.76, 4.16, 4.08),
  d0 = 1 mm; all match.
- **SI pp. 11, 13 (pages 18, 20)**: 2.5 and 1.5 % per hour, 200 and 70 cells, 10^4 pL, ~1 h, ~1 pL, 2 and 1 %
  per hour; all match.
- No transcription error was found in `data.yaml` or in any model; nothing was corrected.
- `added.yaml` is empty and nothing the models use is unstated: It's normalisation comes from SI footnote 6
  (recorded as `q_It_normalisation`), and the chick stage behind the tension ratio is a recorded reading
  (`q_tension_stage`).

## Added

- **`magnet_force_bead_scaling`** (new model, p. 10, Table S1 caption): the stated F ∝ rb^3 d^-4, tested as
  F0 ∝ rb^3 with `prefactor: unknown`; data `rb_0122`, `rb_0253`, `rb_0398` (Table S1, p. 10); runs
  `run_F0_rb3_*`; comparisons `cmp_F0_rb3_0122`, `cmp_F0_rb3_0253`, `cmp_F0_rb3_0398` (validation against the
  fitted F0). The d^-4 part has no model (see `q_bead_scaling_extrapolated`).
- **`q_eps0_sign_convention`** (p. 7 against p. 16): Methods writes eps0 = am/at - 1, the SI writes
  at/am = 1 + eps0; the two are inverse.
- **`q_fig_s3_caption_form`** (p. 10): the Fig. S3 caption prints F0 (d/d0)^alpha; the text, the label inside
  the plot and the model use (d0/d)^alpha.
- **`q_table_s1_vs_fig_s3`** (p. 10): at a glance, the plotted curves of Fig. S3 lie several times below what
  the Table S1 F0 (at d0 = 1 mm) give. This is left for the figure job to read; it may explain `q_force_range`.
- **`q_eq1_minimization`** (p. 3): the derivation's energies, substituted as printed, have no minimum in lambda;
  Eq. 1 follows from balancing them.
- **`q_bead_scaling_extrapolated`** (p. 10): which part of the rb^3 d^-4 claim is tested, and that F0 is
  extrapolated outside 2-8 mm.

## Disagreements with the first reader

- None that changes a value or a model. The relation `regime` ranges for ri ([20, 90] um) in `relations.yaml`
  are narrower than the tabulated ri (44-232 um, pp. 4-5); that is a judgement of the first reader and is left as
  it is, with the question `q_relation_regime_ri`.
