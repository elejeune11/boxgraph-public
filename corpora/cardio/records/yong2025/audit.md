# Audit of yong2025 (second reading, 2026-11-09)

A second, independent reading of `corpus/cardio/2025_Yong.pdf` (PDF pp. 1-17) against the record. Page
images were checked for every equation page (pp. 2-5), Table 1 (p. 7), the Fig. 8 caption (p. 9) and the
supplement tables (pp. 12-15).

## Corrections (transcription errors)

- **rmicro_eq10, coronary_closed_loop, coronary_closed_loop_mean_dsfr, coronary_block_svzerod (Eq. 11, p. 3).**
  The page prints `Rmicro-RCA(t) = [(k_PH sqrt(k_RCA Rbar) - sqrt(0.75 Rbar)) e_n(t) + sqrt(0.75 Rbar)]^2`, with
  k_PH *outside* the square root. The record had `sqrt(k_PH k_RCA Rbar)`, in the equation strings and in the code.
  This is corrected to the printed form in `rmicro_eq10/model.py`, `coronary_closed_loop/model.py` (function
  `r_micro`, which `coronary_closed_loop_mean_dsfr` loads), and `coronary_block_svzerod/model.py`
  (`Ra2_max = k_PH^2 k Rbar` for svZeroDSolver's R_am,max). The equation strings in the three model.yaml files are
  corrected too. Only the PH runs change, because k_PH = 1 in every normal run. Effects:
  - run_rmicro_rca_PH: PH cycle-mean RCA resistance 234.5 (was about 125) against the printed 231.29 (Fig. 3
    caption, p. 5); maximum 902 (was about 361), which fits the Fig. 3B PH axis that runs to 1000.
  - run_cl_vrimp_PH / run_clm_vrimp_PH: RCA mDSFR 6.75 with Eq. 14 (was 5.01) and 3.80 as a ratio of means (was
    2.82), against 5.35 printed (Fig. 8). RCA mean flow falls to 0.84 of normal (printed 0.68/0.80 = 0.85).
- **q_rca_ph_mean (p. 5)**: its text rested on the misread equation ("neither is 231.29"; "k_PH^2 ... would give
  about 235"). It is rewritten with the printed Eq. 11's result, and the first reading is noted in the text.
- **q_ph_rca**: its numbers are updated to the corrected runs, and the old values are kept in the text.
- **source.yaml notes**: the two statements that rested on the old Eq. 11 are updated, and an audit paragraph
  is added.

## Additions

- **mae_*_fig6 (9 data, p. 7, Fig. 6 caption) and mae_*_text (9 data, pp. 5-6, Sec. 3.1)**: the normal-physiology
  MAE values for LAD, RCA and GCV under the three models, printed twice. They are compared pairwise
  (cmp_mae_*_normal, consistency), as the record already did for the PH MAE values. The MAE values themselves
  are still not recomputed: that needs the in vivo waveforms of Fig. 6.
- **q_kph_form (reading, p. 4)**: Sec. 2.5 calls k_PH 'analogous to the 2.5-fold elevation of Emax', but the
  printed Eq. 11 raises R_max k_PH^2 = 6.25-fold. The paper's 231.29 and Fig. 3B support the printed form.

## Checked and found as printed (no change)

- Supp. Table S1 (p. 12), every value, including `1.0 x 10^8` (superscript 8 on the image); the empty column
  headers are confirmed on the image.
- Supp. Table S2 (p. 14), every value. The supplement's Eqs. (1)-(4) (p. 13) are blank on the page image as well
  as in the text (q_supp_equations_missing stands).
- Table 1 (p. 7), all 45 model values and the in vivo values, with their signs (GCV -0.34, -0.42, -0.23, -0.30,
  -0.03).
- Supp. Table S3 (p. 15), every simulated value.
- The Fig. 2 caption (p. 4: 61.31, 42.92, 124.82, k = 2.04; 78.04, 58.53, 144.53, k = 1.85), Sec. 2.3 and 2.5
  (70 %, 75 %, k_PH, 0.6, 0.40 to 1.00, 3.55 to 0.70, 0.04 to 0.41), the Fig. 3 caption (231.29), the Fig. 7 text
  (2.2, 6.3, 1.3, 1.7, 0.68) and the Fig. 8 caption values (p. 9).
- Eqs. 3-6 and 12-14 in coronary_closed_loop match the page images. Eq. 10 matches; the error was only in Eq. 11.
- added.yaml: both added inputs have a basis and real alternatives. No disagreement.

## Disagreements with the first reading (recorded as questions, not changed)

- None beyond q_kph_form, which records why the printed form is kept rather than a disagreement about scope.
