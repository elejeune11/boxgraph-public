# Audit of westerhof1969

Second, independent reading against the page images (`pages/page-NNN.png`).
The page images are about 100 dpi, so they were cropped, rotated and enlarged
(the PDF was not re-rendered). No figures were read.

## Checked, no change

- Table 1 (pp. 6-7, printed pp. 126-127): all 79 rows checked column by column against the page images: dz, r, h, E, C, L_1, R_1 (553 values). No transcription error. These include the unusual-precision entries `s6a_L` "14.34", `s7a_L` "23", `s14b_L` "14", `s15b_L` "19", `s15b_R` "44", `s26aa_R` "24" and `s27b_L` "77", which are printed that way.
- Table 1 D (paired) markers (pp. 6-7): they match the weights in `models/total_length` (6A-12E, 14B-15B, 16A-19A, 24A, 27A, 27B doubled; 13A and 14A not). 79 rows + 42 doubled = 121 segments, as printed.
- `eta_blood` "3 x 10^-2" P, `rho_blood` "1.05", `total_length_printed` "720" (p. 8): match.
- Table 2 (p. 8): `kq_printed` "0.752 x 10^3" (positive exponent), `kt_printed`, `kR_printed`, `kL_printed`, `kV_printed` "0.752 x 10^-6": match. `kC_printed` "10^-3": the superscript is hard to read at this resolution and could be a 6. The OCR writes it "IO+F", the same as for the clearly-3 exponents of time ("lO+sec") and inertance ("lO+H"), while it writes the volume's -6 as "lO-BC". So the record's 10^-3 is kept.
- `Lp_aorta_printed` "0.15", `Cp_aorta_printed` "27 x 10^-6", `Z0_aorta_printed` "≈ 75", `c_aorta_printed` "≈ 5" m/s (p. 23): match.
- `gdz_15cps`, `err_L_printed` "≈ 25", `err_pi_printed` "6" (p. 10): match the text ("about 0.5", "about 25 per cent", "only 6 per cent").
- `tau_normal` 0.8, `tau_stiff` 0.4, `tau_high` 1.66, `tau_low` "≈ 0.5", `k_stiff` 2 (p. 17); `R_high` 3600, `R_low` 850, `R_normal` 1420 (p. 18, Fig. 9 caption): match.
- Models `segment_compliance`, `segment_inertance`, `segment_resistance` (p. 4, Fig. 1 key): C' = 3 pi r^2 (a+1)^2 / (E(2a+1)), L'_n = (rho/S) 1/(2n-1), R'_n = 8 pi eta n / S^2. They match the printed formulas, symbols and factors.
- Models `char_impedance` and `phase_velocity` (p. 23, Eqs. 1 and 3 as approximated there), `lumping_error` (p. 10), `rc_decay` (p. 17) and `unit_translation` (Table 2): consistent with the printed statements.
- Added inputs `k_normal`, `R_high_twice` (alternatives 3600, 3400) and `kp_coefficient`: present with a basis. I have no disagreement.

## Added by the audit

- Model `branch_reflection` (p. 22, Eq. 5, with the bifurcation load of p. 23). Runs `run_Z0_s5c`, `run_Z0_s6a` and `run_reflection_aortic_bifurcation`. Datum `gamma_branch_printed` "≈ 0.1" (p. 22: "mostly in the order of 0.1 or smaller"). Comparison `cmp_gamma_aortic_bifurcation`. Question `q_branch_choice` (kind choice) for the choice of branch point.
- Model `stiffening_increase` (p. 17, "as expected"). Run `run_stiffening`. Data `dZin_stiff_printed` and `dc_stiff_printed`, both "≈ 50" per cent (p. 17). Comparisons `cmp_dZ_stiff` and `cmp_dc_stiff` (approximation). Question `q_stiff_expected` (kind reading): sqrt(2) - 1 = 41%.
- Quantities `reflection_coefficient`, `relative_increase_input_impedance` and `relative_increase_wave_velocity`.
- Datum `dz_range_printed` "2 to 7.5" cm (p. 4) and question `q_dz_range` (unexplained_difference): Table 1 has dz = 1.0 (20A), 7.9 (19A) and 7.7 (27B), outside the stated range.
- Datum `r_individual_printed` "0.15" cm (p. 19) and question `q_radius_threshold` (unexplained_difference): the Discussion says only arteries larger than 0.15 cm in radius are represented individually, but Table 1 has 16 rows with r < 0.15 cm.
- Question `q_impedance_level_85` (kind reading, p. 22). The 85 g cm^-4 s^-1 impedance level (from Fig. 6) is said to equal the proximal-aorta Z0, which p. 140 computes as 75. The first reader left the 85 out because it is read off a figure. I agree with that choice; the question flags it for the figure reading.

## Disagreements with the first reader

- None on values or models. No transcription error was found, so no datum, model or equation was corrected.
