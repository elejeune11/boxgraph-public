# Audit of suga1973 (second reading)

Auditor: boxgraph auditor, 2026-11-02. Values checked against enlarged crops of the
page images in `pages/` (no re-rendering).

## Values checked, no change needed

- Table 2, control (p. 5): all `vd_d*`, `hr_c_d*`, `emax_c_d*`, `tmax_c_d*`, `dpdtp_c_d*` and the
  MEAN ± SD row (`vd_mean/sd`, `emax_c_mean/sd`, `tmax_c_mean/sd`, `dpdtp_c_mean/sd`) match the page,
  including dog 8 heart rate 150 (OCR "1.50").
- Table 2, enhanced (p. 6): all `hr_e_d*`, `emax_e_d*`, `alpha_d*`, `tmax_e_d*`, `beta_d*`,
  `dpdtp_e_d*` (dog 6 = 54, OCR ".54"), `gamma_d*` and the bottom row (`emax_e_*`, `alpha_*`,
  `tmax_e_*` 157 ± 26, `beta_*`, `dpdtp_e_*`, `gamma_*`) match the page.
- Table 1 (pp. 3-4): all `t1_emax_l{1,2,4,5}_d*`, `t1_tmax_l{1..5}_d*` and the P row (`t1_p_*`) match
  the page. The load-3 Emax column is indeed cut at the gutter on p. 4 (`q_load3_emax_cut` is right).
- Abstract (p. 1): `abs_emax_e_*` 12.2 ± 4.5, `abs_emax_c_*` 6.6 ± 1.2, `abs_tmax_*` 191 ± 29 and
  157 ± 26 match the page.
- p. 7: `tmax_hr_epi_mean/sd` 129 ± 56% match the page.
- No transcription errors found; nothing in `data.yaml` was changed.

## Models checked, no change needed

- `alpha_ratio`, `beta_ratio`, `gamma_ratio` (p. 5, Table 2 legend): ratios as defined (beta is
  control/enhanced, as printed).
- `pv_ratio` (p. 5): E(t) = P(t)/[V(t) - Vd] as printed (also p. 1).
- `elastance_normalized` (p. 8): E(t) = Emax·EN(t/Tmax) as printed; not runnable is justified.
- `mean_sd_*`, `paired_t_*` (p. 3 legend: paired t-test), `tmax_hr_epinephrine` (p. 7, from words).
- Independently recomputed: paired t P values (Emax 0.056, 0.337, 0.068; Tmax 0.569, 0.587, 0.554,
  0.653) and per-dog alpha (dog 8: 1.45 against 1.3) agree with `q_ttest_load` and
  `q_ratio_rounding`; the mean of the enhanced Tmax column is 146.4, as `q_tmax_e_mean` says.

## Unstated inputs

- `sd_ddof_added` has a basis and the real alternative (0); no other unstated input found. Excluding
  paced dogs 3, 7, 9 from `run_tmax_hr_epi` is forced (their heart rate did not change, p. 6).

## Additions and disagreements

- Added question `q_audit_unrecorded_measurements` (kind `reading`, p. 7): the paced heart-rate
  results (45 ± 10%, 49 ± 25%; abstract 45%) and the 1 and 4 ug/kg/min results (pp. 7) are left out
  as not reproducible; I would record them as measured data for validation by other papers' models.
  Scope is the first reader's judgement, so nothing was added to `data.yaml`.
- No further printed result reproducible from the paper's own printed inputs was found uncompared.
- Remaining validator warnings (`pv_ratio` never run, `t1_p_emax_l3` never compared) are explained
  by `q_pv_ratio_no_values` and `q_load3_emax_cut`.
