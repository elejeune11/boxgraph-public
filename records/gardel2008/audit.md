# Audit: gardel2008

Second, independent reading of `corpus/2008_Gardel.pdf` (PDF pp. 1-10) against the record.
Auditor: claude-opus-5-5, 2026-11-01.

## Transcription check (data.yaml against page images)

No transcription errors found; no datum was changed.

- v_switch_threshold (p. 1): "8–10 nm/s" matches the Abstract.
- v_range_cell_front, v_distal_lamellipodium, v_lamella, substrate_modulus_range (p. 2): "0 to 30", "∼25", "∼2" nm/s and "1.5–6 kPa" match.
- v_peak_stress_range, v_peak_gaussian_mean (p. 3): "8–12 nm/s" and "∼8 nm/s" match.
- v_ts_mean, ts_mean, sigma_ts_mean, fa_lifetime_cited (p. 4): "12.7 ± 3 nm/s", "3 ± 2 min", "65 ± 28 Pa", "∼17-min" match the Fig. 3 E,F caption and text.
- G_control_carac, G_blebbistatin, G_carho (p. 6): "2,800", "∼1,500", "∼5,400" Pa match the Methods.
- r_high_speed_typical, r_low_speed_typical (p. 10): the page image shows "−0.35 to −0.56" (OCR "20.35 to 20.56") and "0.34 to 0.5"; the record has the signs right.

## Models

- switch_speed_claim (p. 1, p. 5): the paper prints no equation; the model is the stated words (v at maximal traction = Vc). It matches the Abstract and the Vc of p. 5. No change.

## Added inputs

- The record has no `added.yaml`; no unstated input is needed by the one model. No change.

## Printed results not yet compared

- No other printed result is produced by a model in the paper. The record's only comparisons are consistency checks of the stated threshold; the validator's warning "no reproduction comparisons" is correct for this experimental paper.
- Figures are still not read. In this audit session, too, `boxgraph figure page` and `pdftoppm` were refused by the permission settings, so Fig. 4 D (right), Fig. 5 G and Fig. 3 E,F, which test the threshold claim most directly, could not be added (q_figures_not_read stands).

## Values not added (format limitation)

- p. 3: "F-actin speeds at FAs ranged from 0 to ∼30 nm/s" (CA-Rac cells) and p. 4: ts "varying from ∼5 to 50% of the ∼17-min FA lifetime". Both are approximate ranges, which the printed-value parser (`boxgraph/precision.py`) does not accept ("cannot read a number"). They were entered and then withdrawn rather than reprinted in another form. A later pass can add them if the parser learns approximate ranges. They feed no model and would get no verdict in any case.

## Open questions added (questions.yaml)

- q_vts_before_peak (reading, p. 4): ts is the time when stress *first exceeds* 75% of its maximum (Fig. 3 D caption), so v(ts) is a speed during strengthening, before the peak. This bears on whether cmp_threshold_vs_vts compares like with like and may explain q_threshold_vs_vts. This is a disagreement with the first reader's choice of comparison, recorded as a question; the comparison is left in place.
- q_not_significant_untested (overstated_claim, p. 5): "vs and vw were not significantly altered (Fig. 5 G)" names no test, with n = 3 cells per condition. By eye, vs lies above vw in every condition, and 8-10 nm/s falls between them.
- q_supplement_units (possible_error, pp. 8-9): Fig. S1 legend "50 mM blebbistatin" (50 μM elsewhere and in the panel label) and Fig. S2 legend "2.7 mm" (beside "2.7–8 μm"). Recorded as printed, not corrected.
- q_fig_s3_va (possible_error, p. 10): the Fig. S3 legend uses "va", which is defined nowhere in the paper.

## Disagreements with the first reader

- cmp_threshold_vs_vts (p. 4): see q_vts_before_peak. Not changed.
