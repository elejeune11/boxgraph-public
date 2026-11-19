# Audit of shyer2015

Second, independent reading against the page images (2026-11-18). No transcription error was found; no
datum, model or added input was changed.

## Values checked (all agree with the page image)

- `D_shh_cgs` (p. 14): "1.0x10^-7 cm2/s", minus sign and superscript as shown on the image; OCR drops them. Correct.
- `D_shh_um` (p. 14): "1.0x10^1 μm2/s"; OCR reads μ as m. Correct. 1e-7 cm^2/s = 10 um^2/s, so `cmp_D_units` agreeing is right.
- `k_range_low` (p. 14): "2.0x10^-2". Correct.
- `k_range_high` (p. 14): "2.0x10°", a small raised circle, read as 10^0. I read it the same way; the ends are joined by "~" on the image. Question `q_k_high_reading` already covers the glyph.
- `k_representative` (p. 14): "k = 0.2/s". Correct.
- `k_range_span_printed` (p. 14): "three orders of magnitude". Correct.
- `flux_unit` (p. 14): "( = 1 unit)". Correct.
- `source.yaml` page labels: p. 2 = 569 through p. 13 = 580, p. 14-19 = S1-S6. They agree with the page footers.

## Models

- `shh_diffusion_reaction` (p. 17, Fig. S3E): the printed equation is dc/dt = D d2c/dx2 - kc (1-D) and dc/dt = D ∇²c - kc (3-D). The model's equation and boundary conditions (p. 14) match. The model is not runnable, and I agree: there are no mesh dimensions and the output is colour maps in arbitrary units (scale 0-3). The D port in um^2/s matches "simulated with μm as the unit" (p. 14).
- `k_range_span` (p. 14): this model is built from the words. It is consistent with the printed text.

## Printed results not yet compared

- None found. A text search of every page found no mechanical or geometric number: no modulus, thickness, wavelength, curvature, villus spacing or aspect ratio. The aspect ratios of Fig. S3 are said to be measured (p. 14) but are not printed. Scale bars, culture durations (24, 30, 36 hr), reagent concentrations and the measurement-box sizes (5 um, 100 um, p. 7) feed no model. The first reader's statement that the paper makes no mechanical claim of its own holds (`q_no_mechanics`).

## Unstated inputs

- `added.yaml` is empty. That is consistent, because the only model is not runnable and `k_range_span` takes only printed values.

## Disagreements and added questions

- Added `q_k_span_inclusive` (reading, p. 14). "Three orders of magnitude" may count the decades the range touches (10^-2, 10^-1, 10^0), and under that reading there is no misprint. The first reader's `q_k_span` (possible_error) is kept unchanged beside it.
- The plotted measurements are still unread (`q_figures_unread`). I did not read figures in this audit, as the task directs.
