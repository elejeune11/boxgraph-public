# Audit of smith2004

This is a second, independent reading of PDF pages 2-10 of `corpus/cardio/2004_Smith.pdf`,
checked against the page images. Figures were not read in this job.

## Checked, no change

- Every number in `data.yaml` matches the page image: digits, sign, exponent, unit and page.
  - `A_driver`, `B_driver`, `C_driver` (p. 4): A = 1, B = 80, C = 0.27, N = 1.
  - `Pth_normal` (p. 8): the image shows "(−4 mmHg)", and the OCR drops the minus sign. The record already has -4, and the abstract on p. 2 agrees.
  - `Pth_raised`, `co_decrease_printed` (p. 8): 0 mmHg and 9%.
  - `pao_*_printed` (p. 2): 120/80 to 165/130 mmHg. Fig. 10 (p. 9) agrees by eye.
  - `HR_printed`, `Vtot_printed`, `sv_typical`, `pao_*_typical` (p. 7).
  - `ppa_*_typical`, `pvc_typical`, `ppu_typical` (p. 8).
  - `vspt_swing_printed`, `vspt_swing_pct_printed` (p. 7).
  - `sv_fig7_label` (p. 8, Fig. 7).
  - The L = 10^-6 mmHg s^2/ml in `q_single_chamber` (p. 7) is a negative exponent, as the image shows.
- `driver_eq5` matches Eq. 5 (p. 4) as printed, with N = 1.
- `closed_loop` and `two_chamber` match Eqs. 1, 2, 5-18 and 20 as printed (pp. 4-7).
  - The Eq. 20 residual has the sign structure of P_spt = P_lvf − P_rvf (Eq. 15, p. 6).
  - P_th enters only through P_peri (Eq. 14).
  - Inertia (Eq. 7) is used only at the aortic and pulmonary valves, as Fig. 1 and the text of p. 5 state.
  - The valve law follows Sec. 2.4.2 (p. 6).
- `co_decrease` and `scale_resistance` match the text (p. 8, p. 2).
- `added.yaml`: every input the paper does not state is there with its basis. The choices that can move a verdict (`C_closed_added`, `pth_pulm_added` and the two-chamber boundary pressures) have alternatives. The CellML parameter values have none; this is the first reader's judgement and is covered by `q_parameters_unstated`.

## Changes

- Added datum `sv_rv_fig7_label` (p. 8, Fig. 7). The right-ventricle panel of Fig. 7 also carries the label "SV=70", and the record compared only the left-ventricle label.
- Added output `SV_rv: sv_rv_normal_pred` to run `run_closed_normal`. The model already produced SV_rv.
- Added comparison `cmp_sv_rv_fig7` (reproduction, `sv_rv_normal_pred` against `sv_rv_fig7_label`).
- Added question `q_baseline_fig7_vs_fig8_9` (unexplained_difference, pp. 8-9).
  - By eye, the baseline in Fig. 7 (V_lv about 45-117 ml, P_lv peak about 125 mmHg) differs from the baseline loops of Figs. 8 and 9 (about 130-140 ml, about 135 mmHg).
  - The record uses one baseline run for all of these comparisons.
- Added question `q_vein_resistances` (unstated_model, p. 6). Sec. 2.3 names vein resistances "Rpu and Rvc" that are absent from Fig. 1 and from every equation.
- Added question `q_eq19_inlet_inertia` (reading, p. 6). Eq. 19 puts inertia on the single chamber's inflow as well as its outflow, which bears on `q_inlet_inertia`.

## Disagreements (not changed)

- `closed_loop` and `two_chamber` (p. 7): the text says "the initial flow rates are calculated using Poiseuille's equation as given in Eq. (6)". The models start both inertial flows at 0. The results are taken at a periodic steady state, checked by `ref_closed_beats` and `ref_two_chamber_beats`, so this should not matter. I left it as the first reader's numerical choice (see `q_numerics`).
