# Audit of mekhdjian2017

A second, independent reading against the page images (pp. 4, 6, 7, 8, 24-29, 34). Figures were not
read or rendered in this audit.

## Checked, no change

- Fig. 5b parameters `nm_range_5b`, `nc_range_5b`, `Fm_5b`, `vu_5b`, `kon_5b`, `koff_5b`, `Fb_5b`, `kc_5b`
  (p. 7): digits and units agree with the table image (250-500, 2 pN, 120 nm/s, 150-500, 0.3 s^-1, 0.1 s^-1,
  2 pN, 0.8 pN/nm).
- Fig. 5c-d labels `nm_low_5c`, `nc_low_5c`, `nm_high_5c`, `nc_high_5c` (p. 7): 250/150 and 500/500 agree.
- Fig. S4b parameters `nm_s4`, `Fm_s4`, `vu_s4`, `nc_s4`, `kon_s4`, `koff_s4`, `Fb_s4`, `kc_s4`, `Fthresh_s4`,
  `kadd_range_s4`, `ncmax_s4` (p. 34): agree with the table image (150, 2 pN, 120 nm/s, 150, 0.3 s^-1,
  0.1 s^-1, 2 pN, 0.8 pN/nm, 12 pN, 0.01-1 s^-1, 750).
- Fig. S4c-d legend `kadd_0`, `kadd_001`, `kadd_01`, `kadd_1` (p. 34): 0, 0.01, 0.1, 1.0 /s agree.
- `Fthresh_5` (p. 27, 5 pN), `E_gel_27` (p. 4, ∼2.7 kPa), `Lnucleus` (p. 25, 5000 nm), `n_events_text`
  (p. 28, 10^6: the superscript is clear on the image; OCR "106"), `t_sim_text` (p. 28, approximately
  10,000 s), `E_opt_text` (p. 6, ∼10 kPa): agree.
- `motor_clutch_reinforced` against Eqs. 4, 5 (pp. 24-25), 10-12 (p. 27), 13 (p. 28): Tcell = Fsubstrate/(π
  radhesion^2), Esubstrate = 9 κsubstrate/(4π radhesion), nthreshold = Σ(Fclutch,i > Fthreshold), favailable =
  (nclutch,max - nclutch(t))/nclutch,max, k*add = kadd nthreshold favailable, Δt = -log(URN)/Σki; new clutches
  join unbound at xsubstrate (p. 28). The code follows the equations as printed.
- `spread_area_pss` against Eqs. 6-9 (pp. 25-26): equation string agrees with the images, including Eq. 8's
  vretrograde/Lactin - vprotrusion/Lactin; marked reconstructed by the first reader, which stands.
- `total_force_product` against the Fig. 5 legend (p. 7) and `traction_optimum` against p. 6: agree.
- Reference `ref-ghibaudo2008` (p. 30): page range "1846-1843" is as printed, kept.
- Added inputs `r_adh_added`, `Atot_added`, `vpoly_added`: each has a basis and an alternative. Not changed.

## Changes

- `source.yaml` `pages`: added the journal page labels of PDF pages 9-22 (1475-1488), visible in the page
  footers (pp. 9-22). The map stopped at page 8.
- `runs.yaml`: added `run_opt_fig_low` and `run_opt_sim_low` (the peak modulus of the Fig. 5c solid line, as
  plotted and as simulated), p. 7.
- `comparisons.yaml`: added `cmp_Eopt_low_fig` and `cmp_Eopt_high_fig`, the simulated peak positions of both
  Fig. 5c curves against the plotted ones. The Fig. 5c caption (p. 7) claims more motors and clutches "shifts the
  peak traction to a higher stiffness"; the record compared the dashed curve's peak only with the text's ∼10 kPa.
- `questions.yaml`: added `q_mts_stiffness` (unstated_input, p. 8): the paper tests the reinforcement model
  against the molecular-tension-sensor surfaces ("effectively much stiffer than PA gels", Fig. S5) and rejects it,
  but gives no modulus for those surfaces, so the test cannot be run in the record.

## Disagreements (no change made)

- None with the transcription. The judgements of the first reader (radhesion and [Actin]Total inferred from the
  Fig. S4c-d plateaus, the steady-state area model, taking the Fig. S4e orange line to be the kadd = 1.0 /s run,
  leaving Fig. S5 unread) are recorded with their questions and were left as they are.
