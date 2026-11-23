# Audit of owen2017 (second reading, 2026-11-22)

Second, independent reading of `corpus/motor_clutch/2017_Owen.pdf` against the record, from the page images.
Figures were not read (that is the next job's).

## Values checked against the page images (no transcription errors found)

- Table 1, all 15 rows (p. 6): means, SEs, lag times (10 ± 1, 3.4–6 min) and track counts all match; data `t1_*` unchanged.
- Results-text duplicates `txt_*` (pp. 5, 6, 7): match the page.
- Table S1 speeds `s1_*` (p. 20): 119/53/223/70 measured, 90/53/149/77 corrected match the page.
- Clutch-model inputs and results (pp. 23, 41): Ftot = 1000 pN, Ct = 500, κ = 1 pN nm^-1, k0 = kon = 1 s^-1, αc = -0.15 / -0.6 / 0.6, v = 1.7, ~0, 220 nm s^-1 match. The αc units on p. 23 (pN^-1 nm^-1, s^-1 pN^-1) and p. 41 (pN^-1 s^-1) are as `q_alpha_units` says.
- Continuum stiffness (p. 20): r = 0.5 μm, E = 10 kPa, 5 nN/μm match. `k_node_max` ~24 nN/μm, `E_node_printed` ~50 kPa, `E_bulk_*` ~200 / ~300 Pa (p. 8) match.
- Fig. S10 caption (p. 34): 90 Pa, Poisson 0.5, 270 Pa match.
- Network inputs (pp. 12–13): ~40 μm, ~15 MPa, 2 MPa, 14.5 MPa, 320 nm, l = 10 μm, κ ≈ 2.4 × 10^-6, 2 × 10^-8, 2 × 10^-5 match; the exponents are right.
- The settings of `fiber_network_point_load` (2.8–3.4 lattice spacings, 0.1 short-element cutoff; pp. 12–13) match.

## Models checked against the printed equations (no changes)

- `clutch_velocity_eq13` (p. 22, eqns 11 and 13; again on p. 8): the code is eqn. 13 as printed, with the stated condition v = 0 for k0 ≤ −αc Ftot/Ct (p. 23). My own arithmetic gives 1.657 at −0.15, 0 at −0.6 and 220.0 at 0.6.
- `clutch_velocity_eq14` (p. 23): matches the printed eqn. 14, including both branches.
- `off_rate_slip_eq6`, `off_rate_catch_eq7` (p. 21): match, with β = 1/kBT.
- `continuum_stiffness`, `modulus_from_stiffness` (p. 20): read as πEr/[2(1+η)]. The units (Pa·μm → nN/μm, nN/μm / μm → kPa) are right. The ambiguous inline notation is now a question (below).
- `youngs_from_shear` (p. 34), `bending_ratio_persistence`, `bending_ratio_rod` (p. 13, from words), `localization_correction_eq2` (p. 19, eqn. 2): match the printed text and equation.

## Questions added (no datum, model, added input or question changed or deleted)

- `q_figure_misreferences` (p. 23, p. 13): Supp. p. 6 cites "Fig. S16" for the slip-bond sensitivity of eqn. 13; that is Fig. S17 (S16 is the network). Methods p. 13 cites "Supplemental Figure S15B" for the zyxin–α-actinin-1 subtraction; that is S14 (S15 is VASP).
- `q_raw_or_corrected_velocities` (p. 13 against p. 20): Methods says the reported mean velocities come from corrected displacements; the Supplement says all are raw measured. Table 1's α-actinin-1 mean (63.2) matches neither column of Table S1.
- `q_spooling_rows_imply_fast_zyxin` (p. 6, p. 39): Table 1 rows 6 and 7 imply a mean zyxin speed of 87 nm/min over the 192 colocalized pairs, against 55 nm/min over all 864 zyxin tracks, with plaques faster than actin.
- `q_S1_speed_vs_displacement` (p. 20), disagreement with scope: Table S1's left-out displacements and time resolutions reproduce the τ = 10 min speeds as d/τ, but the τ = 1 timepoint speeds come out 18–27 % below the printed ones. Recorded as a `reading` question, not added as data, because the scope is the first reader's.
- `q_continuum_formula_precedence` (p. 20): "πEr/2(1+η)" is ambiguous; the record's reading gives 5.2 nN/μm, the literal left-to-right reading 11.8 nN/μm.
- `q_node_stiffness_spread` (p. 8, p. 12): the node-stiffness distribution is given only as "differ ... by an order of magnitude", with nothing printed beyond ~24 nN/μm. The lattice spacing (~3 μm) can be inferred from fibre length; the force scale and domain radius cannot.

## Items reviewed and left as they are

- Unstated inputs: `eta_continuum_added` (0.5; alternatives 0.45, 0.3) and `T_added` (310 K; alternative 298 K) have a basis and real alternatives. No other unstated input feeds a run.
- Printed model results: every value the paper says its models produce is compared, except those that cannot be: Supp. eqn. 2's corrected values (inputs not printed, `q_localization_inputs`), the network's `k_node_max` (model not runnable, `q_network_not_runnable`), and Fig. S17 and Fig. 6B (figure job). Eqns 6–7 are never run because no parameter values are printed for them.
- The validator's 9 warnings are these same items; all are explained by existing questions.

Validator: `owen2017: SOUND (0 errors, 9 warnings)`.
