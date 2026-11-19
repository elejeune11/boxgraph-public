# Audit of shyer2013 (second reading, 2026-11-18)

Checked against the page images of PDF pp. 2-7 and 11-15 and the text of pp. 10, 16-26.

## Values (data.yaml): no transcription errors found
- circ_ratio_E8_E12 (p. 2, 0.55), culture_circ_ratio_E6 (p. 2, 0.53): match.
- long_ratio_E13/E14/E15 (p. 3, "about 0.75, 0.69, and 0.55"), culture_length_ratio_E12 (p. 3, 0.66),
  factor_E12_printed (p. 4, "about 1.5"), culture_length_ratio_E15 (p. 4, 0.68), factor_E15_printed (p. 4): match.
- tube_380, tube_300 (p. 3): the page shows µm (the text layer's "mm" is OCR); unit um is right.
- modulus_ratio_chick_text (p. 5, "about 10"), modulus_ratio_mouse_text (p. 7, "about 1.5"),
  modulus_ratio_chick_sim (p. 14, 12), modulus_ratio_mouse_sim (p. 14, 1.5): match.
- modulus_increase_292 (p. 12, "around 15% at α = 292.1º"): match.
- day_*, D_factor_chick (2.7), D_factor_mouse (2.0) (p. 14): match.
- we_over_W, le_over_L (2), wm_over_W, lm_over_L (1.666), hm_over_he_zigzag (he = hm/2),
  zigzag_spacing_sm (W ≈ L = 2.0(he + hm)), area_constant_printed (p. 15): match.
- ratio_*_printed (p. 5, 0.5 and 0.6), zigzag_spacing_main, spot_diameter_printed, spot_growth_printed (p. 5): match.

## Models: all as printed
- stressfree_chick (p. 14): he = (0.13 - 0.1t)D, we = (0.35 + 2.8t - 1.4t²)πD, le = (1 + 0.5t²)L,
  hm = (0.39 - 0.3t)D, wm = 1.5πD, lm = (1 + 0.333t²)L: code matches.
- stressfree_mouse (p. 14): he = (0.2 - 0.1t)D, we = (0.5 + 2t - t²)πD, le = (1.6 + 1.2t - 0.6t²)L,
  hm = (0.2666 - 0.0666t)D, wm = 1.5πD, lm = (1.4 + 0.8t - 0.4t²)L: code matches.
- spot_growth (p. 15): 1 + (e^-η - 0.2)t, η = [r/(3he)]²: constants C = 3, A = 0.2 match.
- nominal_compression, inverse_ratio: as worded (pp. 3-5, 15).
- fe_luminal_patterns (pp. 12-13): W = (µ/2)[Tr(FFᵀ)J^-2/3 - 3] + K(J - log J - 1), K = 3µ, F = AG⁻¹,
  contact Ka²[(h - d)/h]², h = a/3, Δt = 0.1a/√K, m = a³, γ = 10m: settings match.
- fe_modulus_fit (p. 11): meshes 50 × 20 × 40 and 50 × 30 × 40, one eighth, ABAQUS 6.11: match.
  Not added (scope of the first reader): the fit uses only the first 5 to 8 points (p. 11; E10 8, mouse 5, Fig. S3 caption p. 19).

## Changes
- Added question q_circ_ratio_sim_vs_measured (p. 14, p. 2): the chick schedule's wm = 1.5πD gives a
  circumferential ratio of 1/1.5 throughout, against the measured 0.55, although the SM says the
  stress-free states were chosen to approximately yield the measured expansion ratios. Not entered as a
  comparison because the record treats the two as different quantities (the first reader's choice).
- Added question q_zigzag_ratios_source (p. 5): the zigzag simulation's 0.5 (endoderm) and 0.6
  (mesenchyme) are said to be "as measured experimentally (Fig. 3A)", but Fig. 3A gives one composite
  longitudinal ratio per stage.
- Added question q_figS7_panel (p. 21): Fig. S7 caption refers to Figs. 4A and 6C for the circumference
  plot; it is Fig. 4B.

## Disagreements
- None with the first reader's judgements. Printed results the models produce are compared where a run is
  possible; the remaining uncompared printed result (modulus_increase_292) comes from the non-runnable
  ABAQUS fit, as recorded in q_modulus_fit_not_runnable.
- Left as the first reader did: the snake simulations of Fig. S10 (pp. 15-16) are not entered; they have
  printed inputs (mesenchyme stretched 1.5 and 2, endoderm 1.666 and 1.333, µe = 10µm, he = hm/3)
  but no printed numerical result to compare.
