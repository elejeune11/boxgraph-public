# Audit of pries1990

Second, independent reading against the page images (pp. 1, 3-7) and text.

## Checked, no change

- Data, p. 3: `D_main_arteriole` (~35 um), `hd_inflow_A/B/C` (0.56, 0.54, 0.31), `nseg_A/B/C` (913, 546, 436, Table 1): match the page image.
- Data, p. 1: `nseg_B_abstract` "583" is what the abstract prints (checked on the image, not an OCR error).
- Data, p. 5: `ninv_pct_A/B/C` (Table 2, all 18 counts and percentages) and `r2_A_table2` (0.148), `r2_C_table2` (0.333): match.
- Data, p. 6: `W_fig3` (3.5 um), `W_network_A` (4 um), `W_networks_BC` (3.4 um), `r2_A_fig4` (0.15), `r2_C_fig4` (0.33), `nseg_A_fig4`, `nseg_C_fig4`: match.
- Data, p. 7: all 18 Table 3 values (`hd_mean/sd/cv_meas/pred_A/B/C`): match.
- Data, pp. 4, 6: curve labels `hd_fig1_*`, `hd_fig3_*` (0.8, 0.6, 0.45, 0.3, 0.1): match.
- Model `fahraeus_eq1`, p. 4: Eq. 1 as printed (1.7 e^-0.415D, 0.6 e^-0.011D): match.
- Model `viscosity_invitro`, p. 4: Eqs. 2-3 as printed (110 e^-1.424D + 3 - 3.45 e^-0.035D; alpha = 4/[1 + e^-0.593(D-6.74)]; denominator e^(0.45 alpha) - 1): match.
- Model `phase_separation`, pp. 4-5: logit relation and Eqs. 4-6 (-6.96, 6.98, 0.4/DF): match.
- Model `inflow_velocity`, p. 3: v = 0.4 D - 1.9: match.
- Model `viscosity_modified_eq7`, p. 6: checked on an enlarged crop of the page image; Eq. 7 is printed as eta_rel' = eta_rel (D^4/(D - W)), with the 4 on D in the numerator only. The record models it as printed, and the corrected variant `viscosity_modified_eq7_corrected` is kept beside it with `q_eq7_form`: correct handling.
- Text claims on p. 5 (condition 1: NINV 3.0-5.5%, r2 0.06-0.177) and in the abstract (r2 between 0.15 and 0.33) agree with Table 2 / Fig. 4; they are ranges, so not added as data.
- `added.yaml` is empty; no model run in the record needs an input the paper does not print, so nothing is missing there.

## Changes

- Added datum `r2_A_text_p6` (p. 6, "r2HD increases from 0.148") and comparison `cmp_r2_A_text_p6` (consistency with `r2_A_table2`, Table 2 condition 3, p. 5): a printed result not yet compared.
- Added question `q_ninv_1_4_percent` (p. 4, kind `unexplained_difference`): the text says boundary modification reduced NINV to "1-4%" of segments, but Table 1 (p. 3) gives 24 of 546 = 4.4% for network B.

## Disagreements and remarks (no change made)

- `source.yaml` (p. -): `reader.model` is the string "None"; the first reader's model id was not recorded. Left as is (metadata of the first reading, not a transcription).
- Observation for later readers (p. 3, Table 1 vs p. 5, Table 2): NINV after boundary modification (25, 24, 7) equals Table 2 conditions 2 and 5 (uniform viscosity), as expected from the zero-hematocrit check runs; Table 1's NINV columns are outside the first reader's scope, so not recorded as data.
