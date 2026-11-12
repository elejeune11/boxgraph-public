# Audit of campbell2011 (second reading, 2026-11-11)

## Values checked against the page images (no transcription errors found)

- Table 1, p. 3: `bsa_*`, `lbm_*`, `co_*`, `ci_*` all match the image (digits and units).
- Table 2, p. 5: `Lv_*` (1226/1021/1555, 1141/1015/1484), `R_*` (16/14/18, 17/15/18), `w_*`,
  `wB_*`, `wL_*`, `RB_*`, `RL_*`, `Rw_*`, `awc_*` all match.
- Table S1, p. 14: `vegfa_*`, `vegfr1_*`, `vratio_*` match.
- Text percentages, pp. 1, 2, 4 (`awc_excess_*`, `bsa_pct_results`, `lbm_pct_results`,
  `vegfr1_deficit_results`, `vegfa_excess_*`, `vratio_deficit_results`) match.
- Supplement p. 12: `grid_spacing_printed` 40 um, `frame_side_printed` 120 um,
  `grid_point_area_printed` 0.0016 mm2, `squares_per_frame_printed` 9 match.

## Models checked against the printed equations (p. 12)

- `diffusion_radius`: equation string matches the print "√(1 ÷ π x length density)"; the code
  takes π x Lv as the divisor, a reading the first reader recorded as `q_radius_precedence`. I agree
  (the left-to-right reading has the wrong dimension); no change.
- `capillary_length_density`: equation string matches "2 · ∑C ÷ ∑Pt · 0.0016mm2"; not runnable
  (no counts printed), with `q_lv_precedence` and `q_lv_counts`. Agree; no change.
- `grid_geometry`, `size_ratios`, `cardiac_index`, `vegf_ratio`, `female_vs_male_percentages`:
  from words, match the stated relations. No change.

## Additions

- Added data `sw_m_med`, `sw_f_med`, `swi_m_med`, `swi_f_med` (Table 1, p. 3: LV stroke work 78
  and 69 g.m, stroke work index 39 and 40 g.m.m-2 per beat), model `stroke_work_index`, runs
  `run_swi_m`/`run_swi_f` and comparisons `cmp_swi_m`/`cmp_swi_f` (approximation: ratio of
  medians; 78/2.0 = 39, 69/1.8 = 38 against 40).
- Added data `myoarea_m_med`, `myoarea_f_med`, `art_n_m_med`, `art_n_f_med`, `art_d_m_med`,
  `art_d_f_med` (Table 2, p. 5), model `arteriolar_density`, runs `run_artd_m`/`run_artd_f` and
  comparisons `cmp_artd_m`/`cmp_artd_f` (4/3.4 = 1.18 and 4/3.6 = 1.11 against 1.0).
- Added quantities `lv_stroke_work`, `lv_stroke_work_index`, `myocardium_area_per_section`,
  `arterioles_per_section`, `arteriolar_density`.
- Added question `q_arteriolar_density_ratio` (unexplained_difference, p. 5): the ratio-of-medians
  gap for arteriolar density and women's stroke work index.
- Added question `q_capillary_density_other_papers` (unexplained_difference, p. 12): batch-10
  cross-paper check. Diffusion radius 16-17 um here against the 12.0 um domain radius of
  rakusan1992's adult controls (2249/mm2), and Lv 1226 mm/mm3 (at most ~1226 profiles/mm2 in
  cross section) against 2249 (rakusan1992), 2301-3157/mm2 (kaneko2011) and the 2000-4000/mm2
  mammalian range. Recorded as a finding with what differs (method, orientation, age, CAD), not as
  an error. No comparison entry: the other records' data cannot be referenced from this record's
  comparisons, and a cross-record `validations.yaml` belongs to the later relate/validate job.

## Disagreements and remaining items

- None with the first reader's judgements.
- `lbm_m_med`/`lbm_f_med` stay uncompared (validator warning): height and weight per group are not
  printed (`q_lbm_inputs`).
- Fig. 2 (p. 5) remains unread; it is for the figure job (see figures.md).
- Mohammed2015's controls have no data yet, so no comparison with them was possible.
