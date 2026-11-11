# Audit of wan2002 (second reading, 2026-11-10)

A second reading of every page against the record: page images of pp. 2-8 opened, text of pp. 1-12.
No transcription errors were found; nothing was corrected. Two additions.

## Changes

- **Added datum `left_iliac_diameter_reduction`** (p. 6): "the left iliac artery has a 50% reduction in
  diameter". This is the only printed stenosis dimension of the aorto-iliac case; it was missing. It comes
  with a new quantity `stenosis_diameter_reduction`. No run uses it: the stenosis length and proximal
  diameter are not printed (q_examples_not_runnable).
- **Added question `q_eq41_index`** (reading, p. 5): Eq. 41 sums over C but prints the summand with an
  undefined index i (Q_i^in, Q_i^out). The record reads it as Q_C, as in Eq. 42.

## Checked and found as printed

- `data.yaml`, all values against the page images:
  - `n_poiseuille`, k1 2 x 10^7, k2 -22.53 and k3 8.65 x 10^5 (units g s^-2 cm^-1 and cm^-1), Kt 1.52 and
    the 32 of Kv (pp. 2-3).
  - Single segment: r0 0.4 cm, L 16 cm, L/D 20, 16 elements, 100 steps, three cycles (p. 6).
  - Bifurcation: 50, 16 and 17 elements of 1 cm (p. 6).
  - Treatment plans: 200 steps over five cycles (p. 7).
  - Costs: 500,000 and 500 degrees of freedom, 25,000 and 5 cpu minutes (p. 8); "roughly 5000 times" (p. 2).
  - Table I (p. 7): all 60 entries agree with the page image, including the nine minus signs that the
    OCR renders as "2".
- Models against the printed equations:
  - `profile_terms_eq6` matches Eq. 6, and `profile_terms_eq3_5` matches Eqs. 3-5 as printed. Re-derived
    for general n: Eq. 3 on the profile of Eq. 5 gives 1/(1 + n), and Eq. 4 gives -2(n + 2) pi, without the
    factor nu (q_eq4_viscosity stands).
  - `pressure_area_eq11` matches Eqs. 11-14, and `stiffness_eq14` matches Eq. 14.
  - `wave_speed_eq21`: the eigenvalue of A (Eq. 21) at Q = 0 with Eq. 11 gives c0^2 = (2/3)(Eh/r0)/rho. A
    and G (Eqs. 21, 23) follow from Eq. 2 via Eq. 18. C (Eq. 27) gives CU = G.
  - `stenosis_dp_eq15` matches Eqs. 15-16. `stenosis_dp_eq17` matches Eq. 17; with Q0 = Q1 it gives the
    same Dp as Eq. 15.
  - `flow_difference_table1`: 100 (1D - 3D)/3D.
- The paper against the release:
  - The theory notes (docs/source/content/theory.rst) print Eqs. 1, 2, 11, 14, 21, 33 (tau) and 34 (|B|)
    exactly as the paper does.
  - Eq. 8 (p - QR = 0): the release's RESISTANCE outlet takes an optional distal pressure Pd. With the
    one-row table the record writes, Pd = 0 (Code/Source/cvOneDSubdomain.cxx, lines 317-324), so the
    outlet is the paper's p = QR.
  - The OLUFSEN card's field order (inputFileGuide.rst, line 247) matches the adapter's
    (`single_segment_svoned/oned.py`). The viscosity passed is dynamic (nu rho), as the guide requires.
  - The coded law (cvOneDMaterialOlufsen.cxx, lines 137 and 200) is Eqs. 11 and 14.
- Settings of `single_segment_svoned` and `bifurcation_svoned`: the printed mesh, step count and cycle
  count are used, and the unprinted settings are listed in q_quadrature.

## Disagreements

None with the first reader's judgements. The added values (density, viscosity, reference pressure,
resistances, bifurcation radii) all have a basis and alternatives.

## Noted, not changed

- The abstract (p. 1) says "All of these solutions were obtained in less than 5 min of computation time".
  This is the same bound as `cpu_1d` (p. 8), so no new datum was added.
- The porcine bypass "on the order of 50%" and "less than 10%" peak differences (p. 8) are read off
  Fig. 5. They are left to the figure stage, as the first reading says.
