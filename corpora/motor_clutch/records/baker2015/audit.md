# Audit of baker2015 (second reading, 2026-11-21)

Scope: the text and page images of PDF pages 1-21. No figures were read or rendered (left to the figure job).
Page images were cropped and enlarged to check the Methods equation and the Fig. 2c labels.

## Transcription checks (no errors found)

- All 30 data in `data.yaml` checked against the page images (pp. 2, 3, 4, 8): digits, signs, units and pages
  agree with print. No value changed. This includes the moduli of pp. 2-4, the Fig. 3a labels (0.3 kPa, 19 kPa),
  the Fig. 2c fibre doses (6,000 mJ, 0 mJ), the collagen moduli (<0.3, 1.1 kPa), and the membrane parameters of
  p. 8 (20 um, 1 mm, 0.25 mm, 0.5; wells 2 mm; cylinders 500 um).
- `membrane_indentation` (p. 8): the equation as printed is F = E t pi delta^3 (ro^2 - ri^2) / (2 (ro - ri)^4 (1 - nu)).
  The model matches it in every symbol, sign and factor. Its units are consistent: the result is in N, returned as mN.
- `source.yaml` page map (pp. 1-7 -> 1262-1268; SI pp. 10-21 -> 1-12): checked on pp. 2-6, 12. It agrees.

## Additions

- `uv_intensity_gel`, `gel_time_soft`, `gel_time_intermediate`, `gel_time_stiff` (p. 8, Methods hydrogel
  preparation): the gel UV intensity and polymerization times. They were missing.
- `uv_gel_soft_fig2c`, `uv_gel_stiff_fig2c` (p. 3, Fig. 2c labels "Soft (750 mJ)", "Stiff (3,000 mJ)"): the gel
  doses. These were missing (only the fibre doses were recorded).
- Model `uv_dose_exposure` (dose = I t, marked `reconstructed`: the paper never writes the product). Runs
  `run_dose_gel_soft/intermediate/stiff` and comparisons `cmp_dose_gel_soft` (750 vs 750),
  `cmp_dose_gel_stiff` (6,000 vs 3,000) and `cmp_dose_gel_intermediate_vs_stiff_label` (3,000 vs 3,000). See
  q_gel_stiff_dose.
- `gel_soft_fig4_caption`, `network_soft_fig4_caption`, `fibre_soft_fig4_caption` (p. 5, Fig. 4b caption) and
  `gel_soft_suppfig6`, `network_soft_suppfig6` (p. 16, Supp. Fig. 6 caption): repeated statements of the soft
  conditions. Each is checked against the Fig. 3 caption by the consistency comparisons `cmp_gel_soft_fig4`,
  `cmp_gel_soft_suppfig6`, `cmp_network_soft_fig4`, `cmp_network_soft_suppfig6` and `cmp_fibre_soft_fig4`.
- `collagen_fibre_modulus_lit_min/max` (p. 2): the literature range of 0.5-10 GPa for collagen fibres (refs 12, 14),
  which the paper compares its fibre moduli with.
- Quantities `uv_intensity` and `exposure_time`, and a new `runs.yaml`.

## New open questions

- `q_gel_stiff_dose` (possible_error, p. 8 vs p. 3): the Methods give 60 s at 100 mW cm-2 (6,000 mJ cm-2) for stiff
  gels, but Fig. 2c labels the stiff gel 3,000 mJ, which is the Methods' intermediate gel.
- `q_membrane_magnitude` (unexplained_difference, pp. 8, 12): a rough check that is not a verdict. With E = 55 kPa,
  the printed membrane equation gives about 0.01 mN at 100 um. Supp. Fig. 2k shows about 0.5 mN, rising about
  linearly with depth. The figure job should read Supp. Fig. 2k and run the model.
- `q_dexma_conc_units` (possible_error, pp. 2, 8 vs 17, 18): the DexMA spinning concentration is given as g ml-1
  in the Methods and Fig. 1b, but as mg/ml in the Supp. Fig. 7 and 9 captions.

## Disagreements with the first reader (recorded as questions, nothing changed)

- `q_gel_range` -> `q_gel_range_dose` (reading, p. 8): the soft gel's 750 mJ cm-2 dose is below the lowest dose in
  Fig. 1e (1,000 mJ cm-2). The 290 Pa soft gel lying below the 450 Pa end of the range is therefore expected and
  probably not a misprint. q_gel_range is kept as written.

## Not changed

- `added.yaml` does not exist: no input is added, because the only model run here (`uv_dose_exposure`) uses
  printed values only. The membrane model still has no run, because its force and depth inputs are only plotted
  (q_membrane_inputs_plotted). The validator warns about this, correctly.
- The figure data remain for the figure job (q_figures_not_read). The most important are Fig. 5c-f for cao2017
  and Supp. Fig. 2k for membrane_indentation.

Validator: `baker2015: SOUND (0 errors, 2 warnings)`. The warnings are "membrane_indentation never run" and "no
reproduction comparisons", both expected until the figures are read.
