# Audit: biot1963

Second reading of every page against the page images (pp. 5, 6, 9, 10, 11, 12, 13, 14 for equations
and numbers; text of pp. 1-4, 7, 8, 15).

## Checked, no change

- `zeta_crit_printed` (p. 6, Eq. 2.10): 0.839 matches the image; also printed in Eqs. 4.2 and 4.13 (pp. 11, 14).
- `lambda_plane_printed` (p. 11, Eq. 4.3): 0.543 matches.
- `P_plane_printed` (p. 11, Eq. 4.4): 3.08 mu0 matches.
- `lambda_uni_printed` (p. 14, Eq. 4.14): 0.444 matches.
- `P_uni_printed` (p. 14, Eq. 4.15): 2.05 mu0 matches.
- `k_crit_printed` (p. 14): k = 0.295 matches.
- `table1_mu`, `table1_rigidity` (p. 13, Table I): all 9 index values and 18 entries match the image,
  including the leading-dot forms (.90, .543, .28) and the final 0.
- `char_cubic` (p. 5, Eq. 2.9): zeta^3 + 2 zeta^2 - 2 = 0 matches.
- `decay_k_eq28` (p. 5, Eq. 2.8): k = sqrt((1 - zeta)/(1 + zeta)), zeta = P/(2 mu) matches.
- `incremental_modulus_plane` (p. 9, Eq. 3.25): mu = (1/2) mu0 (lambda^2 + 1/lambda^2) matches.
- `plane_compression` (p. 11, Eq. 4.1): P = mu0 (1/lambda^2 - lambda^2) matches.
- `crit_stretch_plane` (p. 11, Eq. 4.2): (1 - lambda^4)/(1 + lambda^4) = 0.839 matches.
- `surface_rigidity_plane` (p. 13, Eq. 4.10, with Eq. 4.8 on p. 12): matches as printed.
- `k_plane_eq411` (p. 14, Eq. 4.11): k = lambda^2 matches.
- `uniaxial_compression` (p. 14, Eq. 4.12): P = mu0 (1/lambda - lambda^2) matches; consistent with
  Eq. 3.28 (p. 10).
- `crit_stretch_uniaxial` (p. 14, Eq. 4.13): (1 - lambda^3)/(1 + lambda^3) = 0.839 matches; consistent with
  Eqs. 3.28-3.29 (p. 10).
- `k_uniaxial` (p. 14): the superscript is not legible at page-image resolution; the first reader's 3/2
  follows from Eqs. 2.8 and 4.13 and is already questioned in `q_k_uniaxial_exponent`. No change.
- `added.yaml`: none; agreed, every quantity in the paper is a ratio to mu0 and no input is unstated.
- Existing questions (`q_rounding_critical_values`, `q_table1_mu_rows`, `q_table1_rigidity_rows`,
  `q_strain_one_half`, `q_penetration_depth`) agree with my own hand checks.

No transcription errors found; nothing corrected.

## Added

- Quantity `rigidity_factor_phi` (pp. 12-13): phi of Eqs. 4.7-4.8, distinct from mu phi/mu0.
- Model `phi_eq48` (p. 12, Eq. 4.8 with Eq. 2.8): phi from zeta, as printed.
- Datum `phi_crit_printed` (p. 13): the printed result "At this critical value we find phi = 0", not
  compared before.
- Runs `run_phi_crit` (from the printed zeta = 0.839) and `run_phi_cubic` (from the computed root of
  Eq. 2.9), with comparisons `cmp_phi_crit` (reproduction) and `cmp_phi_cubic` (consistency: the paper's
  statement that phi = 0 has the same real root as the cubic, p. 13).

## Disagreements and new questions

- `q_phi_unstressed_branch` (reading; p. 12): `surface_rigidity_plane` hard-codes phi = 1 at zeta = 0, so the
  lambda = 1.00 row of Table I is reproduced by assertion rather than by the formula (which is 0/0 there;
  its limit is 1). Left as the first reader wrote it.
- `q_phi_zero_weak_test` (reading; p. 13): the printed "0" carries a +/- 0.5 digit interval, so the new phi
  comparisons are weak tests; the algebraic equivalence with Eq. 2.9 holds exactly.
