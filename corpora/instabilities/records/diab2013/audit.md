# Audit of diab2013

Second, independent reading against the page images (pp. 1, 2, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16).
No transcription error was found; nothing in the record was changed except one added question.

## Data checked (no change)

- `eps_B_printed` (p. 5): 0.456, as printed; also pp. 1, 2, 6 (Fig. 2 caption), 11, 13.
- `eps_M_printed`, `kbar_M_printed` (p. 8): 0.272 and 1.30; agree with pp. 1, 5, 6, 7, 11, 13 (1.3 on p. 12).
- `kbar_fig4a` (p. 9): 0.628, as printed; the other FEM frames 1.30 and 2.51 are left out by the first reader (noted in source notes).
- `eps_w_fem` (p. 9): eps_w(i) = 0.157 at kbar_w(i) = 0.628, as printed.
- `eps_T_printed`, `kbar_T_printed` (p. 12): 0.174 and 0.471; agree with pp. 1, 13.
- `eps_R_printed` (p. 12), `kbar_R_printed` (p. 10): 0.593 and 0.107; agree with p. 13.
- `crease_lower_bound_homogeneous` (p. 11): 0.35, as printed.
- `hohlfeld_crease_vanishing`, `hong_crease_strain`, `gent_cho_crease_strain` (p. 2): 0.35, 0.35, 0.28-0.42, as printed.
- `crease_tip_strain_fem` (p. 13): 0.456, as printed.

## Models checked (no change)

- `bifurcation_wavenumber_eq28`, `bifurcation_strain_eq28`, `biot_strain_eq28` (p. 5): Eq. 2.8 is transcribed as printed (numerator 4 lambda^2 sqrt(3 - 2 lambda^4 - lambda^8), three denominator factors with the printed signs); eps = 1 - lambda as stated on p. 5.
- `m_point_eq211` (pp. 5-7, 14-16): Eq. 2.6a (alpha_m, sgn(5 - 2m), (-1)^m), Eq. 2.6b (Omega_m), Eqs. 2.5a-c, A 4, A 6c-d (Phi, Theta), A 9a solution forms, A 10, A 11a-b (C1 with 1/k as printed, already questioned in `q_A11b_k`), Eq. 2.11 and Eqs. 2.12a-b (factor -2 on 2.12a, factor 1 on the p(2) term of 2.12b) all match the page images.
- `m_point_eq211_corrected`: a variant with the evidence stated; I agree with its argument (the second derivative of -p(J - 1) in the direction (u(2), p(2)) gives the mixed term twice). Kept as the first reader wrote it.

## Added inputs

- `added.yaml` is empty; the only unstated choices (Q0 = a = 1, collocation and scan settings) are recorded as the `choice` question `q_second_order_coefficients` and in the run notes. Agreed: the sign of the energy variation does not depend on Q0 or a.

## Uncompared results

- The T-point, R-point and crease-tip strain warnings are FEM results with no runnable model (`q_fem_not_runnable`). No further printed result produced by the paper's analytic models was found uncompared: the remaining numbers (kbar = 1.30, 2.51 FEM frames; kbar < 0.15; the range 0.272 < eps < 0.456) repeat recorded values or are FEM settings.

## Added

- `q_hohlfeld_source` (reading, p. 11; p. 2): p. 11 attributes the 0.35 consistency to Hohlfeld & Mahadevan [18], whereas the 0.35 compared (`hohlfeld_crease_vanishing`) is printed on p. 2 for Hohlfeld [8]. The datum keeps ref-8 as printed.

## Disagreements

- None with the first reader's judgements.
