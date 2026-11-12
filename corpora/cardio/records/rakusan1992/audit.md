# Audit of rakusan1992 (second reading, 2026-11-11)

Checked every value in `data.yaml` against the page images of pp. 1-6 (Tables 1, 3, 4, 5, the Fig. 2 and
Fig. 3 legends, the text percentages) and every model against the Methods (p. 3) and legends (p. 5).
No transcription error was found: digits, signs, the exponent of `cd_poly_a3` (-6.76 x 10^-6, p. 5), the
sign of `da_poly_b2` (-0.001, p. 5) and all units match. The models are the paper's statements as printed.
Nothing was changed or deleted.

## Additions

- `myo_frac_inf_text`, `myo_frac_older_text` (p. 4): the text's rounded myocyte area fractions
  "87% versus 82%", not recorded before; compared with Table 3 in `cmp_myo_text_inf`, `cmp_myo_text_chi`,
  `cmp_myo_text_adu` (consistency).
- `q_audit_halfway_radius` (reading, p. 3): the Methods also define the Krogh radius as "the mean distance
  halfway between two capillaries", which is not 1/sqrt(pi CD); the first reader's model is kept.
- `q_audit_abstract_differences` (possible_error, p. 1): the abstract gives the coarctation group as 15-39 y
  (15-30 y in Methods and Table 5) and p<0.05 for the infant-to-children density decrease (Table 3: p<0.01).
- `q_audit_cross_record_density` (unexplained_difference, no page): normal adult capillary density here
  (2,249/mm^2) against kaneko2011 (2,301-3,157), mohammed2015 controls (median 1,044) and campbell2011
  (a length density, not comparable); what differs is listed. Comparisons across records cannot be
  entered in this record.
- `q_audit_no_blood_volume` (unstated_input, p. 3): why no model turns these densities into a blood volume
  fraction to set against vink2024 (capillary luminal area not measured).

## Disagreements (left as judgements of the first reader)

- `q_domain_radius_definition` / `krogh_radius` (p. 3): see `q_audit_halfway_radius` above.
- The "sixfold increase in heart weight" (p. 6) was left out as hedged; "approximately" may govern only
  the 10-fold body weight. Not added (255/40 = 6.4 would agree with it either way).
- Fig. 1 legend densities (p. 4) left out as single fields; agreed.
