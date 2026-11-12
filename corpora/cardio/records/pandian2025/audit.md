# Audit of pandian2025 (second reading, 2026-11-12)

The page images were checked against `data.yaml`, the models and the questions. The PDF was not rendered and no
figure was read. The Fig. S5 colour-bar labels were checked only by enlarging the existing 110 dpi page image.

## Values checked, no change

- p. 4: `r2_diam_inhouse` 0.967, `r2_diam_muves` 0.857, `r2_diam_reaver` 0.589 match the page image. The
  eccentricities are printed "~0.8" and "~1" (`q_eccentricity` writes them without the tilde; this does not
  change the point).
- p. 5: `v_avg_network` "about 100 um/s", `diameter_range` 20 to 40 um, `media_head` 4 mm and the bead size
  "10 um diameter" match.
- p. 7: `wss_avg_network` "about 0.1 dynes/cm2", `r2_wss_regression` 0.864, `v_outlet_grid_a` 72.4 and
  `v_outlet_grid_b` 24.1 mm/s, and `dp_grid_printed` "~18 Pa" (the tilde is on the image) match.
- p. 9: `needle_single_channel` 160 um and `needle_network_device` 250 um match. The network gel holds HUVEC
  (3 million/mL) plus HLF (1 million/mL) in 2.5 mg/mL fibrin, as the `preparation` condition says.
- p. 10: `region_side_pixels` 255, `region_side_comsol` 906 and `bead_diameter_methods` 10 um match.
- p. 11: these match the page image: `rho_media` 1000 kg/m3, `mu_media` 1.002 x 10^-3 Pa s (exponent -3),
  `eps_fibrin_endo` and `eps_kappa_formula` 0.265, `kappa_fibrin_control` 1.2e-7 (superscript 31 is the
  citation), `pd_control_printed` 5e-8 and `pd_il1b_printed` 50e-8 (unit printed m2/s), `mu_endo_printed`
  3e-3 (unit printed Pa), `L_between_channels` 1 mm, the four inlet pressures 3.15, 1.75, 0.35 and 0.075 Pa
  ("of the control" printed twice), and `p_out` 0 Pa.
- p. 11: `grid_parent_channel_diameter` 250 um and `grid_vessel_diameter` 50 um match. p. 17, Fig. S5a: R = 25
  and R = 125 um, t = 10 um, as the note says.

## Models checked, no change

- `kappa_from_pd` (p. 11): kappa ≈ P_d mu L / eps_p, as printed.
- `forchheimer_cf` (p. 11): C_f = 1.75 / sqrt(150 eps_p^3), as printed.
- `pd_dextran` (p. 10): P_D = (2 r_vessel / I_vessel) dI_gel/dt, as printed, with the citation superscript 24
  confirmed.
- `poiseuille_tube`, `wss_from_velocity`, `hydrostatic_head`, `pressure_range`: these are the reader's checks.
  Their code was checked by hand: 97.6 um/s, 0.26 dyn/cm2, 39.2 Pa and 5.66e-13 m2, as `source.yaml` says.

## Unstated inputs

- `pd_control_mps`, `pd_il1b_mps`, `mu_endo_pas`, `r_vessel_added`, `L_path_added` and `g_added` all have a
  basis and alternatives that could change a verdict. No disagreement.

## Transcription errors

- None found. No datum, model or added input was changed.

## Questions added

- `q_ns_sign` (p. 11, possible_error): the Navier-Stokes equation is printed with a minus sign before the
  divergence, `= -div[-pI + mu(...)]`, unlike the Brinkman equation below it. This was checked on the page
  image. It is not a model in the record, so no model was changed.
- `q_s5_vmax_digits` (p. 17, reading; disagrees with the first reading of `s5c_v_max` and `s5b_v_max`): at
  110 dpi, the IL-1beta velocity colour-bar maximum read as 22.4 could be 72.4, the value printed in the text.
  The control 29.1 could be 24.1. If so, `q_outlet_velocity` largely resolves. The values are kept as first
  read; the figure pass should settle them at high resolution.
- `q_pd_factor` (p. 10, possible_error): the printed factor 2r in P_D is four times the r/2 (= d/4) of the
  usual cylindrical form (ref. 26's protocol, not in the corpus).
- `q_pd_citation` (p. 10, reading): the P_D formula cites ref. 24, which is an image-analysis paper; ref. 26
  may be meant.

## Printed results left uncompared

- `v_outlet_grid_a`, `v_outlet_grid_b` and the Fig. S5 colour-bar labels (pp. 7, 17): the grid CFD is not in
  the record, so nothing in it computes them. They are set against each other in `q_outlet_velocity` and
  `q_s5_vmax_digits`.
- The R2 values (pp. 4, 7): these need the plotted points (Fig. 2a) or the regression coefficients
  (`q_wss_regression`). They are for the figure pass.
- The "~3-5 dynes/cm2" physiological range (p. 7, ref. 26) and the "approximately 85%" of WSS variance
  (p. 7) were left out by the first reader. Neither is a result of a model in the record; this is not
  disputed.

## Relations with the human sources

- No relation was added, and the first reader's reasons are agreed. The corpus's tissue capillary morphometry
  has no like-with-like quantity printed here. The Pries viscosity laws are for blood and do not apply to the
  culture medium (1.002e-3 Pa s). The "whole blood" viscosity of 3e-3 Pa s cites refs. 32 and 33 (the authors'
  own vein models, not in the corpus), so it is not set against the Pries laws.

# Figure pass (2026-11-12)

Calibrated readings of Figs. 2a, 2b, 3c, 3e, 3f, 3h, 3i and 4a-c, 4e-g were added. See `figures.yaml`, `figures/`
and `figures.md`. The pass added data, models (`r2_linear_fit`, `pd_by_group`, `group_mean_points`), runs,
comparisons and the questions `q_figures_read` ... `q_fig2a_r2_line`. Nothing existing was deleted.

## Change to an existing datum

- `s5c_v_max`: printed "22.4" was changed to "72.4". The label was first read from the 110 dpi page image
  (`q_s5_labels`, `q_s5_vmax_digits`). Rendered from the PDF at 1200 dpi, the upper end of the Fig. S5c velocity
  colour bar plainly reads 72.4, with "mm/s" above it. This was a transcription error, not a correction of the
  paper. The other S5 labels were confirmed unchanged. Recorded in `q_s5_labels_1200dpi`.

## Note for the tools

- A unit with a numeric factor, such as `1e-6*cm/s`, is accepted by `boxgraph.units.parse_unit`, but the factor
  is silently dropped (only the units of the parsed quantity are kept). Fig. 4a was therefore read in nm/s.
