# Audit of chilian1986 (second reading, 2026-11-06)

## Values checked, no change needed
- Tables 4 and 5 (p. 8): all 60 values `t4_*` and `t5_*` match the page image: digits, ± SE, mmHg, and the class diameters in the `where` fields.
- Table 6 (p. 9): all 24 values `t6_*` and their n values match (including n = 7 for control large arterioles).
- Table 3 (p. 6): `t3_map_ctl`, `t3_map_pap`, `t3_mbf_ctl`, `t3_mbf_pap` match.
- Abstract (p. 1): `abs_mbf_ctl` (139 ± 9), `abs_mbf_pap` (339 ± 52), `abs_map_*`, and the claims `abs_*` match the image.
- Results (p. 5): `res_prox_200_ctl`, `res_pct_70_130_ctl`, `res_prox_70_130_ctl`, `diam_*`, `dchange_*` match. The OCR "MO-220" is "180-220" on the image, as the note says.
- Results/Discussion (p. 6): `res_prox_lart_pap`, `res_prox_mart_pap`, `disc_prox_venules_ctl`, `disc_prox_100ven_pap` match.
- No transcription errors found in `data.yaml`.

## Models checked, no change needed
- `pressure_percent_of_aortic` (p. 5, Table 6), `resistance_partition` (p. 5, the 70%/30% rule), `segment_resistance_fraction` (p. 1), `pressure_drop` (p. 1), `coronary_resistance` (p. 4, "quotient of mean aortic pressure and myocardial blood flow"), `relative_diameter_change` (p. 5): each matches the paper's words. All are from_words, and the paper prints no symbolic equation for any of them.

## Added (printed results not compared before)
- `disc_prox_175_200_ctl` (p. 6, "approximately 25%", control) + `cmp_prox_175_200_ctl_disc` against `prox_ctl_mart`.
- `disc_prox_75_130_ctl` (p. 6, "approximately 50%", control) + `cmp_prox_75_130_ctl_disc` against `prox_ctl_sart`.
- `disc_prox_175_200_pap` (p. 6, "only 10%", papaverine) + `cmp_prox_175_200_pap_disc` against `prox_pap_mart`.
- `disc_drop_100_ctl` (p. 8, "about 30 mmHg less" in arterioles < 100 um) + `cmp_drop_100_ctl_disc` against `drop_ctl_sart`.
- `disc_gt100_ctl` (p. 9, "about 50% ... in arterioles greater than 100 um") + `cmp_gt100_ctl_disc` against `prox_ctl_sart`.
- `impl_prox_100_ctl` (p. 9, "approximately 50% ... proximal to arterioles 100 um") + `cmp_prox_100_ctl_impl` against `prox_ctl_sart`.
- `impl_prox_200_ctl` (p. 9, "about 25% ... about 200 um") + `cmp_prox_200_ctl_impl` against `prox_ctl_mart`.
- `impl_prox_200_pap` (p. 9, "only about 10% ... proximal to 200 um", papaverine) + `cmp_prox_200_pap_impl` against `prox_pap_mart`.
- Not added: the Fig. 5 and Fig. 6 captions (p. 7: venule ~8/0 mmHg, arteriole ~20 mmHg below aortic). Each comes from one tracing, not a group mean.

## Questions added
- `q_prox_100_ctl_rounding` (pp. 1, 5, 6, 9): the share proximal to the 100-um arterioles is 45% in the abstract, 45-50% in the results and ~50% in the discussion. Table 4 gives 43.6%.
- `q_size_class_mapping` (pp. 1, 5, 6, 8, 9): the paper names the medium and small arteriole classes by several different size ranges. The record maps every statement to the Table 4/5 classes.

## Judgements of the first reader, left as they are
- `added.yaml` is empty. The zero outflow pressure is built into `resistance_partition` and recorded as `q_outflow_pressure_zero`. I agree: the paper's own 70%/30% rule (p. 5) implies it, so I raised no question.
- Approximate printed claims ("~25", "≈ 90" and the added "≈" values) get no verdict, by design.
