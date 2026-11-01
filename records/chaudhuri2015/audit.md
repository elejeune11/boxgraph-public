# Audit of chaudhuri2015

Second, independent reading by an agent (claude-opus-5-5), 2026-11-01, against the page images in
`pages/`. Re-rendering at higher dpi was not possible in this session, so I checked everything at
page-image resolution.

## Values checked, no change needed

- `koff_table`, `Frup_table`, `vu_table`, `Fstall_table`, `kon_table`, `kclutch_table`,
  `initial_adhered_length_table`, `E1_range_table`, `E2_range_table`, `eta1_range_table`,
  `eta2_range_table`, `ligand_density_range_table` (p. 17, Supp. Table 2): digits, units and sources
  match the image (0.1 s^-1, 2 pN, 120 nm s^-1, 150 pN, 1 s^-1, 5 pN nm^-1, 1 μm, 0.01-100 pN nm^-1
  twice, 0.01-100 pN s twice, 0.004-0.02 ligands nm^-1). The reference numbers 9, 10, 11, 1/12, 1, 13
  and 7 match `references.yaml`.
- `dt_note` (p. 20): 0.2 ms matches.
- `nc_5` … `nc_1000` (p. 8, Supp. Fig. 1d labels): 5, 25, 50, 100 and 1000 match.
- The damping values quoted in `q_eta_values_units` (p. 3, Fig. 1 caption: 5 × 10^-13 and
  1 × 10^-13; p. 6, Fig. 5b: 1x10^-12, 5x10^-13, 1x10^-13) match the images. So does the
  η1/η2 naming conflict in `q_eta_names`.

## Models checked, no change needed

- `bell_off_rate` (p. 18): k*off = koff e^(Fclutch/Frup) matches the printed form.
- `retrograde_flow_eq1` (p. 19, Supp. Eq. 1, and v_spread = vu − v_retrograde): matches.
- `burgers_eq2` (p. 19, Supp. Eq. 2): matches as printed, including η2/E2 on d²σ/dt² and
  (η1²η2/(E1E2)) dε/dt d²ε/dt² on the right side. I checked the superscript 2 on η1 at page
  resolution only. I agree with `q_eq2_form`.
- `clutch_springs_nolattice` (p. 21) and `lattice_spreading` (pp. 18-21): their scope and from-words
  rules are the first reader's judgement and are left unchanged. The code follows the rules listed in
  `q_s1d_rules`.
- `bell_off_rate` and `retrograde_flow_eq1` carry "never run" warnings. They produce no printed result
  of their own (they are used inside `clutch_springs_nolattice`), so there is nothing to compare.

## Additions (printed inputs the record left out)

- `n_steps_note` (p. 19): the run length of 60,000 time steps, entered as "60000" because the
  printed-value syntax has no thousands separator. This fills the declared but unused quantity
  `n_time_steps`.
- `n_steps_lead_spacing` (p. 20): the 60,000-step averaging window for the lead node spacing.
- `s1c_duration`, `s1c_n_runs` (p. 9, Supp. Fig. 1c caption): 1 s of simulated time and 20 runs.
- `s1e_ksub`, `s1e_ligand_density` (p. 9, Supp. Fig. 1e caption): k = 1 pN/nm and 0.02 ligands/nm.
- `s1f_strain_rate` (p. 9, Supp. Fig. 1f caption): 0.17 nm/ms.
- `fig1_lig_6`, `fig1_lig_56`, `fig1_lig_100`, `fig1_lig_225`, `fig1_lig_400` (p. 3, Fig. 1b-d curve
  labels, lig μm^-2). 100 appears only in Fig. 1c,d.
- New quantities `ligand_area_density`, `tensile_extension_rate`, `simulated_duration` and
  `n_simulation_runs`, for the data above.
- No new runs or comparisons. The paper gives no numerical model result in the text. Its model
  results are curves in Fig. 1b-d, Fig. 5b and Supp. Figs. 1c, 1e, 1f and 2, and all of these rest on
  the lattice model, which cannot be run (`q_lattice_unstated`). The one result from a runnable model,
  Supp. Fig. 1d, is already compared.

## New open questions

- `q_ligand_density_measures` (pp. 3, 9, 17, possible_error): Fig. 1 labels its curves with an area
  density (lig μm^-2), while Supp. Table 2 gives a line density (nm^-1), and the paper never says how
  the two map. If the area density is the square of the line density, the label 6 lig μm^-2 lies below
  the printed range.
- `q_experimental_scope` (pp. 3-4, 9-16, reading): **disagreement.** The first reader left out the
  measured data (Figs. 2-4, Supp. Table 1, Supp. Figs. 3-5), but the guide asks for every plotted
  measurement to be read. I did not add them in this audit.
- `q_s1d_xaxis_audit` (p. 8, reading): at page resolution I see the same label/tick mismatch on the
  Supp. Fig. 1d x axis that `q_s1d_xaxis` describes. I could not re-render the panel, so the tick
  calibration is not independently verified, and no run uses the alternative calibration.

## Transcription corrections

- None: no value or equation was found entered differently from what is printed.
