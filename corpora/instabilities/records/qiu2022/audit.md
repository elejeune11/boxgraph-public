# Audit of qiu2022 (second reading, 2026-11-18)

Checked against the page images of PDF pages 2-4 (figures not re-read; that is the next job).

## Values checked, no change
- alpha_fig2 (p. 4, Fig. 2 caption): "α ≈ 0.005" matches the image.
- alpha_range_ecoli (p. 2): "0.001 < α < 0.01" matches.
- phat_0_4_p3, khat_w_p0_4 (p. 3): "p̂ = 0.4", "κ_w R ≈ 0.2" match.
- pbar_zero_p3, kbar_w_p0, kbar_B_p0 (p. 3): "p̂ = 0", "κ̄_w = 1.320", "κ̄_B = √(8/3) ≈ 1.633" match. pbar_zero_p3 is
  printed as p̂ = 0 and entered as p-bar = 0, the same value; noted, not changed.
- flattening_brazier, moment_reduction_brazier (p. 3): "about 22%", "about 40%" match.
- phat_absent_p4, khat_w_unpressurized (p. 4): "0.6%(1/R)" matches.
- Fig. 2 curve labels (p. 4): p̄ = 0, 2.5, 5, 7.5, 10 and p̂ = 0.02, 0.05, 0.1, 0.2, 0.4 match the image.
- No transcription errors found in data.yaml; nothing was corrected.

## Models checked, no change
- torque_shell_eq8, torque_balloon_eq8 (p. 3, Eq. 8): match the printed form, α² in the balloon form.
- brazier_shell_eq9 (p. 3, Eq. 9): matches √(8/3 + 8p̄/9).
- wrinkling_eq11 (p. 3, Eq. 11): matches 8(α² + p̂/3)(p̂/2 + 2α − κ̂_w) + (2κ̂_w/3 − 4α)κ̂_w² = 0. I checked that its p̂ = 0
  limit in κ̄ = κ̂/α is the printed cubic κ̄³ − 6κ̄² − 12κ̄ + 24 = 0, and that its α → 0 limit is the printed κ̂³ − 4p̂κ̂ + 2p̂² = 0.
- wrinkling_eq11_shell: a correct change of variables (κ̂ = ακ̄, p̂ = α²p̄, Eqs. 3-4).
- energy_numerics_balloon (p. 2, Eq. 2 divided by S_z R): the stretching, bending and both pressure terms match Eq. 2.
  The closed-form elimination of Δε0 is correct. I did not check energy_numerics_shell or wrinkling_numerics_* line by line.
- cross_section_brazier (p. 3): I worked the first-order shape by hand. Height 2 + 4a2/3 gives 22.2%; the second moment
  π[(1 + a2/2)² + a2²/36] gives a 30.2% reduction. Both agree with the model.
- Eq. 7 (p. 3): the OCR reads "8(α + p̂/3)"; the image shows α². The record has it right.
- Legend "Equation (9)" / "Equation (12)" in Fig. 2 (p. 4): confirmed on the image (q_legend_equation_numbers).

## Additions
- New model wrinkling_balloon_limit (p. 3): the printed balloon limit κ̂_w³ − 4p̂κ̂_w + 2p̂² = 0, smallest positive
  root. It is a distinct printed equation that the record did not have.
- New model wrinkling_balloon_leading (p. 3): the printed κ̂_w = p̂/2 + O(p̂²), keeping the leading term only.
- Runs run_wlimit_p0_4, run_wleading_p0_4, run_wlimit_fig2b_crosses and run_wleading_fig2b_crosses, with
  approximation comparisons cmp_wlimit_p0_4, cmp_wleading_p0_4, cmp_wlimit_fig2b_crosses and
  cmp_wleading_fig2b_crosses. They test the paper's balloon limit against the "≈ 0.2" (p. 3) and against the plotted
  Eq. 11 crosses (p. 4).

## Disagreements and new questions
- q_audit_alpha_text_statements (reading, p. 3-4): the two text results get the caption's α ≈ 0.005 as a datum, but
  no α is printed with them. I would have entered it as an added input with alternatives (0.0045 and the range
  0.001-0.01). I left the first reader's choice in place. The "≈ 0.2" at p̂ = 0.4 may come from p̂/2.
- q_audit_second_moment_definition (reading, p. 3): my hand calculation confirms the 30% (first order). It equals the
  classical Brazier expansion at ζ = 2/9, so the printed 40% does not follow from either. This supports
  q_second_moment.
- added.yaml is empty. Apart from the point above, I found no unstated inputs. The numerical settings (N, grid,
  optimizer) are recorded as a choice question (q_numerics_settings) and refined.
- Not added, by agreement with the first reader: p̄ = O(10⁴) and the "order of the inverse cell radius" (orders of
  magnitude only, no verdict); Eq. 6 (no printed number); the strain limit 0.2.
