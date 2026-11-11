# Audit of davies2006 (second reading, 2026-11-10)

Checked against the page images of PDF pp. 2-7 and the text of pp. 2-12. Figures were not read (left to the
figure job).

## Values (data.yaml)

- No transcription error found. Checked against the page images: every value on p. 3 (n, age, 62 injections,
  5.1 ms delay and CI, 5 ms advance, 1 kHz), p. 4 (rho = 1050 kg m^-3), p. 5 (septum 0.94 ± 0.2 and
  1.4 ± 0.1 cm, 146 ± 23 / 81 ± 13 mmHg, 148/82 ± 21/9 and 143/80 ± 26/16 mmHg, velocities 0.43 ± 0.52 and
  0.42 ± 0.35 m/s, replicate SDs 5.2 mmHg 3%, 1.9 mmHg 2.5%, 0.057 m/s 10%), p. 6 (55%, 30%, 22.3%,
  0.51 ± 0.45 and 0.14 ± 0.16 m/s, r = -0.52, 0.51, 0.64, -0.15, 0.64, -0.61, slopes 0.53 and 1.98, 2.8% and
  0.97%), p. 7 (all 18 entries of Table 2, signs and column multipliers x10^5 and x10^3), p. 2 (abstract 94%,
  33.1% and 26.9%), p. 11 (age range 35 to 75).

## Models

- wave_separation, single_point_wave_speed, wi_separated, wi_net (p. 4): match the printed equations,
  including the leading minus of WI- and the 1/(4 rho c) factor. No change.
- wave_share, relaxation_share, accelerating_share, pooled_*, replicate_percent_*, slope_ratio, cumulative_wi:
  arithmetic stated in words; consistent with the text. No change.

## Added by the audit

- p_fsuction_septum (p. 6): the printed P = 0.08 for r = -0.15, entered as a derived datum; with model
  correlation_p_value (t test of a Pearson r), run run_p_fsuction_septum, comparison cmp_p_fsuction_septum,
  added input n_correlation_added (20, alternative 10; the paper does not say over which subjects), new
  quantity p_forward_suction_share_vs_septum. r = -0.15 with n = 20 gives P of about 0.53, not 0.08.
- q_p_fsuction_septum (p. 6), kind possible_error: the above, plus the inequality P values that sit just past
  their printed bounds (r = 0.51 gives about 0.022 vs P < 0.02; r = 0.64 gives about 0.0024 vs P < 0.002),
  which get no verdict and are not entered.

## Disagreements and notes (no change made)

- Batch premise that mynard2014 computes coronary wave intensity and may compare with this paper: its text
  contains no wave intensity result; its ref. 15 is Davies et al.'s single-point wave-speed paper (this paper's
  ref. 19), not this paper. This agrees with q_validation_candidates; no validation is added.
- mynard2015 does cite this paper (its reference list names Manisty, p. 15 of that record) and plots coronary
  wave intensity only in its Fig. 7, whose model is not runnable; agreed with q_validation_candidates.
- q_figures_not_read describes Fig. 3 as "one normal subject"; the caption (p. 5) does not say the subject is
  normal (Fig. 5's subject is the LVH one). Minor; left as written.
- q_wia_not_run: agreed that the analysis cannot be run on printed values. Once the figure job digitizes the
  Fig. 3-5 pressure and velocity traces, the derivative steps (Savitzky-Golay window, beats averaged) remain
  unstated, so a rebuilt Table 2 would rest on added choices.
- The velocity P = 0.95 (p. 5) is about 0.96 by an unpaired t test, within the rounding of the printed means;
  not entered.

Validator: SOUND (0 errors).
