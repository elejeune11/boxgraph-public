# Audit of chirat2013 (second reading, 2026-11-14)

## Values checked against the page images (no change)

- `E_mantle` (p. 7): 0.8 MPa matches the page.
- `w_mantle`, `h_mantle` (p. 7): w = h = 0.7 mm match the page.
- `L0_mantle` (p. 7): "~1 cm, so we take L0 = 1 cm" matches the page. The value used is 1.
- `Kf_adhesion` (p. 7): 0.008 MPa matches the page.
- `mode3_si` (p. 7; also p. 2): mode 3 matches the page.
- `g_fig3_left/middle/right` (p. 3, Fig. 3 caption): g = 1, 4, 8 match the page.
- `eta_si` (p. 7): η = 50 matches the page.
- Units and powers of ten: none are garbled. The OCR's "0:8" and "0:008" are decimal points, and the record has them right.

## Models checked against the printed equations (no change)

- `second_moment_si1` (p. 7, SI Eq. 1): I = wh^3/12 is as printed.
- `kf_scaling` (p. 5): kf = Kf L0^4/EI is as printed, and the conversion of cm to mm is correct (kf = 5000 at the SI values).
- `clamped_rod_buckling` (p. 5, reconstructed): the linearization of the printed Eq. 4
  (θ' = γm, m' = γ(nx sinθ − ny cosθ), ny' = γkf(y − py), with nx = −P) gives y'''' + P y'' + kf y = 0, so the sign is consistent with Eq. 4.
- `spine_growth_simulation` (pp. 3, 5, 6): Eq. 1 / Eq. 6 is read from the images as
  Eb = 1 − b1 exp(−((s0 − 0.5)/(2 b2))^2), and b2 = b20/γ (p. 6). This agrees with the record and with `q_eq1_form`.
- `infinite_rod_foundation`: this is the reader's added textbook limit. It is labelled `reconstructed` and is not compared, which is acceptable.

## Printed results not yet compared

- None found. The paper prints no other number that its models produce. Pages 1–6 contain only qualitative claims and the drawn simulation shapes. The counts of genera and families on p. 1 feed no model.

## Unstated inputs

- `added.yaml` is absent. The only unstated items are the assumptions of the reconstructed analysis (γ → 1, clamped ends one pregrown length apart, how modes are counted). These are not numeric inputs, and they are recorded as `q_clamped_x_bc` and `q_mode_selection`. I agree with this.

## Changes made

- Added question `q_eq2_moment_balance` (possible_error, p. 5). Eq. 2's printed M' = NX X' − NY Y' does not reduce to Eq. 4's m' = γ(nx sinθ − ny cosθ); Eq. 2 probably has X' and Y' swapped.
- Added question `q_fig4_readable` (reading, p. 3). Disagreement with `figures.md`: Fig. 4's stiffness panel has numbered axes (Eb 0.5–1.0, s0 0.2–1.0), and its minimum (≈0.52 at s0 = 0.5) could give b1. The Fig. 3 panels also have numbered s0 axes. `figures.md` is the first reader's text and was not edited; this is left to the figure job.

## Notes for the relation jobs (no change)

- p. 2 says the model follows "the general framework of Moulton et al. (21)" (moulton2012, in the corpus). `relations.yaml` is empty because no model of moulton2012 is in this record, so a later job can add the relation.
