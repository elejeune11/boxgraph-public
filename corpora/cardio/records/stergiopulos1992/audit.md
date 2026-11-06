# Audit of stergiopulos1992

Second reading of the record against the page images (PDF pp. 1-12). Figures were not rendered or read.

## Checked, no change

- Table 1 (p. 4): all 55 rows of `L_*`, `rp_*`, `rd_*`, `Cv_*` agree with the page image digit for digit; the
  unit 10^-6 cm^5 dyn^-1 is entered correctly as cm^5/Mdyn.
- Table 2 (p. 5): all 28 `RT_*` and `CT_*` agree with the page image, mantissa and exponent (e.g. `RT_10`,
  `RT_24` E+11; `RT_34` E+09; `CT_26`, `CT_34`, `CT_36`, `CT_38` E-09; `CT_10`, `CT_24` E-11); units N s m^-5 and m^5 N^-1.
- Scalars: `Ctot_burton` 1.0, `Csum_printed` 0.835, `Cres_printed` 0.165, `p0_printed` 97, `R1_ratio_printed`
  ~0.2 (p. 3); `Ls_abdominal` 1.5, `LD_abdominal_printed` 1.6, `Ls_femoral` 2, `LD_femoral_printed` 4.8,
  `stenosis_94` (p. 5); `rt_reduction_94_printed` ~80 (p. 6); `dt_max_printed` ~0.001 (p. 2); PI values and
  ratios 5.5, 1.3, 1.5, 0.3, 0.236, 0.200 (p. 8); `sys_ratio_normal_printed` 1.1 to 1.2 (p. 9). All as printed.
- Models against the printed equations (pp. 2-3): Eq. 1, Eq. 6 with B1 = 8 c_v pi mu/(rho A0), Eq. 7, Eq. 8, Eq. 4
  and Eq. 9 with C0' = K/p0, C1' = -K/(2 p0^2) are transcribed as printed in `arterial_tree_eq4` and
  `arterial_tree_1d`; the windkessel update in `arterial_tree_1d/model.py` is algebraically Eq. 7.
  `eq4_zero_compliance` (dA/dp = A0 K (2 p0 - p)/p0^2), `compliance_sum`, `residual_compliance`,
  `terminal_compliance` (C_Ti = C_vol,res R_total/R_Ti, p. 3), `stenosis_length_ratio` and `pi_ratio`
  (p. 8) match the text.
- `added.yaml`: every added input has a basis and alternatives.

## Changes (additions only; no transcription error was found)

- Added `PI_aorta_gosling` (3.0), `PI_groin_right_gosling` (6.1), `PI_groin_left_gosling` (5.9), p. 8, Fig. 7:
  measured PI labels of Gosling et al. not recorded by the first reading.
- Added `sys_ratio_{thigh,knee,ankle}_fronek_normal` (1.34, 1.26, 1.08), p. 9: measured group means of
  Fronek et al. (1973) for normal subjects.
- Added `sys_ratio_{thigh,knee,ankle}_fronek_aortoiliac` (0.720, 0.698, 0.571) and
  `sys_ratio_{thigh,knee,ankle}_fronek_femoropopliteal` (1.265, 0.728, 0.513), p. 9: measured, recorded only
  (no stenosis severity is given, so no run matches them).
- Added validation comparisons `val_sys_ratio_thigh_fronek`, `val_sys_ratio_knee_fronek`,
  `val_sys_ratio_ankle_fronek`, p. 9: the existing control-case outputs of `run_tree_control` against the
  Fronek normal-subject means.
- Added question `q_fronek_not_compared` (reading), p. 9: why the Fronek data were added.
- Added question `q_fig6_side` (possible_error), p. 8: Fig. 6 legend says "R. Posterior Tibial", the text
  says the left posterior tibial distal to a left femoral stenosis.
- Added one sentence to `source.yaml` notes about the audit additions.

## Disagreements, not changed

- The source notes say the Fronek et al. indices are "measured data that no model here predicts site by
  site"; `arterial_tree_1d` does output the thigh, knee and ankle ratios for the normal case, so the normal
  means are compared (above). The first reader's other choices are kept.
- Not recorded, by the first reader's choice, and left so: the "reduced distal resistance 0.2 x RT" input of
  Fig. 3 (p. 5, "at 20% of the original value") and the approximate critical stenoses of about 85% and 60%
  (p. 5). These are plotted-curve results for the next (figure) job; the approximate values would get no
  verdict.
- The claim on p. 8 that "a PI ratio of 0.2 requires a stenosis with severity greater than 90%" (read from
  Fig. 6) is not compared: it needs the femoral-stenosis series of Fig. 6, left to the figure job.
