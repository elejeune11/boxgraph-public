# Audit of alastruey2011

Second, independent reading of `corpus/cardio/2011_Alastruey.pdf` (PDF pp. 1-9) against the record.
Figures were not read (that is the next job).

## Checked, no change

- `rho`, `mu` (p. 2): 1050 kg m^-3 and 2.5 mPa s, as on the page image.
- `E_silicone`, `Pext`, `phi_measured` (p. 4): 1.2 MPa, Pext = 0, phi = 3.0 ± 0.3 kPa s, as printed.
- Table 2 (p. 4), all 37 rows: every `L_*`, `r0in_*`/`r0out_*`/`r0_*`, `h_*`, `c0in_*`/`c0out_*`/`c0_*`,
  `Gamma_*` and `Rp_*` checked against the page image: digits, units (mm, m/s, Pa s m, GPa s m^-3) and
  page agree. `r0in_28` = "3.9" (one decimal) is as printed. No transcription error found.
- `k_eight`, `phi_24`, `dD_asc_printed` (p. 8): 8 phi, 24 kPa s, "less than 6.5%", as printed.
- `gamma_eq5`, `wave_speed_eq5` (p. 2, Eq. 5): beta = (4/3) sqrt(pi) E h and Gamma = (2/3) sqrt(pi) phi h
  match the page image; c0 = sqrt(beta/(2 rho sqrt(A0))) follows from Eq. 5 at A = A0 (declared `from_words`).
- `network_1d` (p. 2, Eqs. 1 and 5): f = -22 mu pi U, the tube law and Gamma as printed. Its scheme,
  boundary conditions and inflow are the first reader's choices, already in `q_scheme`, `q_bc_junctions`,
  `q_inflow`; not re-judged.
- `added.yaml`: `T_added` (alt. 0.857 s from 70 bpm, p. 7) and `Pout_added` (alt. 0) have real
  alternatives and a basis. The 41 inflow Fourier coefficients have no alternatives; `q_inflow` says why.

## Added

- `quantities.yaml`: `avg_rel_error_pressure`, `avg_rel_error_flow`, `avg_rel_error_pressure_harm_5_20`,
  `avg_rel_error_flow_harm_5_20`.
- `data.yaml`: Table 4 row "All" averages (p. 7) `EP_elas_tab4`, `EP_visc_tab4`, `EQ_elas_tab4`,
  `EQ_visc_tab4`, `EPh2_elas_tab4`, `EPh2_visc_tab4`, `EQh2_elas_tab4`, `EQh2_visc_tab4` (means only; the
  printed SD over sites is in each note, since it is a spread and not an uncertainty of the mean).
- `data.yaml`: the same averages as the abstract prints them (p. 1) `EP_*_abstract`, `EQ_*_abstract`,
  `EPh2_*_abstract`, `EQh2_*_abstract`, and as p. 5 prints them `EP_*_text`, `EQ_*_text`.
- `comparisons.yaml`: 12 consistency comparisons `cmp_*_abstract` (p. 1 vs p. 7) and `cmp_*_text`
  (p. 5 vs p. 7).
- `questions.yaml`: `q_tab4_caption` (possible_error, p. 7): Table 4's caption refers to "Table 2" for the
  error definitions; Table 3 / Eqs. 10-11 seem meant.
- `questions.yaml`: `q_all_sites_claim` (overstated_claim, p. 5): "reduces relative errors ... for all the
  70 measurement sites", while Table 3 (p. 7) shows E_Q tied at 0.0 at Segment 1 and mean-value errors rising
  at Segments 3 and 28.

## Disagreements (recorded as questions, nothing changed)

- `q_tables_not_recorded` (reading, p. 7): the first reader left Table 3 and most of Table 4 out of
  `data.yaml`. They are printed model results; for the eight sites with released waveforms
  (boileau_data) they could be compared by a joining job. Left as the first reader's scope choice.
