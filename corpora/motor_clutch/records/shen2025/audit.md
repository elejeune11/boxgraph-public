# Audit of shen2025 (second reading, 2026-11-21)

Checked against the page images of PDF pp. 3-6, 8-14 (text layer for the rest).

## Values (data.yaml)
- Table I (p. 4): wa, wd0, Nm, kon, koff0, vb, fs, fd, Fb, km, kc, Gamma_kT, l0_printed, tau_printed,
  v0_printed, f_printed match the page image: digits, exponents (893 x 10^-6), units and cited refs. No change.
- F_unloaded (p. 8), ks_stiff (p. 8), g_fig2a / g_fig2d (Fig. 2 panel labels, p. 6), Nc_fig6b / vu_fig6b /
  vu0_Nc10_caption (Fig. 6 caption, p. 9), Nc_fig11_* (p. 11), loadfrac_F0 (Fig. 12 caption, j/10, p. 12): match.
  No change.

## Models
- char_scales, nondim, nondim_stiffness: match the scale definitions on p. 3 (l0 = (kBT/(wd0 Gamma))^1/2, f = (wd0 Gamma kBT)^1/2). No change.
- fixed_point (Eqs. 9-15, p. 4), saddle_node (Eqs. 16-17, p. 4-5), det_eq20 (Eq. 20, p. 5): match as printed. No change.
- stability_boundaries / det_A3: the matrix entries match A3 (p. 14) entry by entry, J55 as printed. I agree with the
  first reader's q_A3_J55 (I derived it independently from A1). No change.
- det_eq18 and limit_cycle: the right-hand side matches Eq. 18 / A1 (p. 5, p. 14) and Eq. 6 (p. 4). No change.

## Transcription errors corrected
- None found.

## Questions added (questions.yaml)
- q_eq7_gamma_factor (p. 4, Eq. 7): Eq. 7 drops Gamma/gamma from the k~s x~s term, the same omission as J55 in A3;
  this supports q_A3_J55 and suggests the gamma != Gamma diagrams may use that form.
- q_tableII_U_row (p. 6, Table II): the second U row (1 positive, 4 negative) contradicts the text (1 negative,
  4 positive) and the sign |J| < 0 on the stable branch.
- q_case2_trivial (p. 5, Case 2; p. 12, Fig. 13(b)): for nm0 f~s - F~ <= 0, Eq. 15 has exactly one positive root,
  not only the trivial one; Fig. 13(b), drawn at F~ = nm0 f~s, shows fixed points everywhere. The record's models
  raise errors there (the first reader's scope; not changed).
- q_amplitude_linear (p. 11, p. 13): "amplitude proportional to v~u0 - v~u" conflicts with the square-root
  growth expected at a supercritical Hopf point; testable with limit_cycle, not run by the audit.

## Disagreements with the first reader (not changed)
- q_ks_fig2a_choice (p. 8): ks = kc for the soft substrate is stated in the text, so ks_soft_added could be a
  reported datum rather than an added input. Kept as entered.

## Printed results not yet compared
- None with a number beyond those already compared. The remaining results are only plotted (Figs. 2, 5-13), left to
  the figure stage (q_figures_not_read). The printed formula F~(w~=1) = Nm f~s/(1 + exp(f~s/f~d)) (p. 12) is Eq. 10 at
  w~ = 1 times f~s; it has no printed value to compare.
