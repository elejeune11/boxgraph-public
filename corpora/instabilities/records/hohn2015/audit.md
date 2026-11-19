# Audit of hohn2015 (second reading, 2026-11-19)

I checked every datum in `data.yaml` that has a printed value against the page images (pp. 1-4, 6-7).
I checked the equations of `shell_inversion` (Eqs. 1-3, S1) and `snap_speed_scaling` (p. 4) against
the printed forms. I did not re-read the figures; the figure job does that.

## Values and equations checked, no change
- nu_printed, eps_printed (p. 3): "nu = 1/2" and "epsilon = h/R = 0.15", as printed.
- lambda_early, kR_early (p. 3): "lambda approx 0.1 pi R" and "kR approx 10-20", as printed.
- rp_realistic, kR_realistic (p. 3): "r_p/R approx 0.7" and "kR approx 20" [13], as printed. The Fig. 4(b) label r_p = 0.7R (p. 4) agrees.
- inversion_duration_range (p. 1): "45 to 80 minutes".
- n_embryos, embryo_diameter_range (p. 2): "10 embryos" and "~70-130 um".
- speedup_factor_measured, U_after_speedup (p. 3): "~5" and "U ~ 0.03 um/s". The Fig. 2(a) inset "5x speed-up" agrees.
- area_decrease_before_t0, area_increase_after_t0, area_final_fraction (p. 3): "~10%", "20%-30%" and "about 55%".
- area_decrease_after_bend, area_decrease_contraction_only (p. 4): "~2.5%" and "~25%".
- area_decrease_median_text (p. 7): "approx 10%", from the Fig. S3 caption.
- e_ratio_early_stage, e_ratio_later_stage (p. 4): "0.97 +- 0.07" and "0.49 +- 0.09", from the Fig. 4 caption.
- shell_inversion (pp. 3, 7): Eqs. 1, 2, 3 and S1 match the page images. In Eq. 3 that includes the prefactors pi E h/(1 - nu^2) and pi E h^3/(12(1 - nu^2)), the integrand weighted by r0 and the limits 0 to pi R.
- snap_speed_scaling (p. 4): force ~ E h^(5/2) e^(1/2)/R, resistance ~ mu U e^(1/2) R^(1/2) and U ~ E h^(5/2)/(mu R^(3/2)) all match the page image. The code uses a prefactor of 1 with `prefactor: unknown`, and its dimensions work out to m/s.
- area_contraction_estimate (p. 4): it is correctly marked `reconstructed`, because the paper prints only the result (~25%).

## Transcription errors corrected
- None found.

## Printed model results not yet compared
- None beyond those already recorded. The paper's other model claims say the shapes agree by eye with
  Fig. 4(f-i), which has no axes (q_shell_not_rerun, q_fig4_shapes_no_axes). The approximate values
  "~10%" (p. 3) and "approx 10%" (p. 7) would get no verdict, so I did not add a consistency comparison.

## Added inputs
- E_sheet_added, mu_fluid_added, R_embryo_added, h_sheet_added (p. 4, for the scaling): each has a basis and
  real alternatives. I have no disagreement with them.

## Open questions added
- q_audit_e0_reference (pp. 2, 4, 6): the paper does not say how e0 is defined for the Fig. 4 e/e0 values,
  compared with t approx -10 min in Fig. 2(a), or at which times the two stages are. Comparisons in
  haas2015 and haas2021 need both.
- q_audit_S1_wording (pp. 6-7): the SM text says the "circumferential stretch vanishes at the equator", but Eq. S1
  gives f_phi0 = 1 there. The printed "kappa_s0 = k > 1" compares a curvature with a pure number, so it
  implies units with R = 1.

## Disagreements with the first reading
- The source notes say the +- on e/e0 are standard deviations over 10 embryos. The caption's "Bars indicate
  standard deviations" refers to the outlines, and the SM averages 20 profile halves (p. 6). I raised this in
  q_audit_e0_reference and did not change the note.
