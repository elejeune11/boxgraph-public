# Audit of kaneko2011 (second reading, 2026-11-11)

Second, independent reading of all 8 PDF pages against the record, with the page images of
pp. 2 and 4 (every printed number of the record is on these pages, repeated in text on pp. 3, 5, 6).

## Transcription checks (no change needed)

- `n_sections`, `section_thickness_6um`, `block_thickness_printed` (p. 2): 200, 6 um, 1.2 mm as printed.
- `terminal_arteriole_d` (p. 2): 15 um. `av_distance` (p. 2): ~350 um.
- `seg_len_mean` (p. 2, p. 4): 61.5 ± 41.6 um, n = 220. `seg_len_art`, `seg_len_ven` (p. 4): 58.9 ± 43.2, 71.1 ± 52.2 um.
- `density_art`, `density_mid`, `density_ven` (p. 2, p. 4 text and Fig. 4 table): 2,301 ± 123, 3,130 ± 501, 3,157 ± 167 /mm2, as printed in all three places.
- `area_art`, `area_mid`, `area_ven` (p. 2, p. 5): 434.6, 319.5, 316.7 um2.
- `sinus_vol_5a/5b/5c`, `cap_sinus_diameter`, `cap_sinus_length`, `sinus_count_density` (p. 2): 20,620 / 14,120 / 4,180 um3, 30-50 um, 50-80 um, ~60,000/cm3.
- `bundle_major`, `bundle_minor` (p. 3, Fig. 2 legend): about 130 by 120 um.
- `necrosis_minor`, `necrosis_major`, `necrosis_length` (p. 3, p. 6): 116.4 ± 13.6, 131.5 ± 31.2 (n = 80), 712.8 ± 47.2 um (n = 53).
- `unit_length_printed` (p. 6; also p. 3 and Fig. 8 legend p. 7): about 700 um.
- Literature values (p. 4-5): `av_rat` 310 (ref. 25), `av_rabbit` 320-380 (ref. 15), `av_pig` 510 (ref. 13), `seg_len_pig` 21.1-54.5, `density_rat_batra` 2,247 ± 112, `area_rat_art_batra` 499 ± 3, `area_rat_ven_batra` 456 ± 5 (p. 5), `density_rat_endo_gerdes` 2,816 ± 72, `density_rat_epi_gerdes` 3,885 ± 71, `density_rw_*` 2,993-4,066, 3,342 ± 40, 1,868-3,037, 2,483 ± 31, `density_rakusan_range` 2,000-4,000: all as printed, with the right reference numbers.
- No exponent or sign errors found; no transcription change was made.

## Models (no change needed)

- The paper prints no equations. `capillary_tissue_area` (A = 1/N, p. 2), `twice_av_distance` ("twofold the arteriolar-venular distance", p. 6; p. 7), `necrosis_equals_bundle` (p. 7) and `serial_section_stack` (p. 2) match the stated words. Unit factors checked (1e6 um2 per mm2; 1000 um per mm).
- Significance claims checked by hand, not entered: a one-way ANOVA with Dunnett's test on the Fig. 4 values, taking n = 3 counting points per side, gives t = 3.2 and 3.4 for middle and venular against arteriolar, above the two-sided 5% critical value (about 2.9 for 2 comparisons, 6 df), so the printed P < 0.05 is consistent if n = 3 (n is not stated: `q_density_n`).

## Printed results not yet compared

- None found among the values the paper derives from its own relations: the three tissue regions, the unit length, the necrosis sizes and the block thickness are all compared.
- Fig. 3 (segment length histogram) remains for the figure job (`q_fig3_not_read`); by eye its bars sum to about 216 and give a mean near 62 um, which a reading can check against n = 220 and 61.5 um.

## Unstated inputs

- `added.yaml` is absent: no model needs an input the paper does not state. Agreed.

## Additions

- `cited.yaml` (new): links `density_rakusan_range` (p. 4) to `rakusan1992/cd_range_mammals`, the same 2,000-4,000/mm2 range as printed on p. 6 of Rakusan 1992.
- `q_density_vs_rakusan_adults` (p. 5): the middle and venular densities are about 40% above the adult control density of rakusan1992 (2,249 ± 85 /mm2); only the arteriolar-side value agrees. Recorded as a finding for the cross-record layer.
- `q_density_vs_campbell_length_density` (p. 2): with capillaries parallel to the fibers, the densities here imply a length density about twice campbell2011's medians, and Krogh radii (10-12 um) well below Campbell's diffusion radius (16-17 um). Methods and patients differ; recorded as a finding.

## Batch notes (no change to the record)

- Capillary lengths against kassab1993: kassab1993 holds the pig arterial trees only (no capillary order), so there is no pig capillary segment length in the corpus to compare with. The pig values the paper quotes are from Kassab and Fung 1994 (ref. 13), not in the corpus; they are compared as quoted (`cmp_seglen_pig`, `q_seglen_pig`).
- mohammed2015 has no record yet, so no comparison with its controls can be named.
- vink2024 (myocardial blood volume): this record has no model of blood volume or vascular volume fraction. The sinus volumes and count could give a sinus blood volume fraction (~60,000/cm3 times 4,000-21,000 um3, about 0.02-0.12%), but the paper states no such relation and does not say which sinuses the count includes (`q_sinus_count_volume`), so none is modelled.
- Disagreements with the first reader: none.
