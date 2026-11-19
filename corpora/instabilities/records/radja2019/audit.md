# Audit of radja2019 (second reading, 2026-11-14)

Checked against the page images: Table 1 (p. 10), Table 2 (p. 11), Table S4 (p. 29), the
text numbers on p. 7-9, Eqs. 1-7 and the simulation settings (p. 18-20), the Fig. 2 caption
(p. 4) and the STAR Methods categories (p. 21).

## Changes

- `rate_ratio_AB_BA` (p. 8): printed changed from `"20"` to `"~20"`. The page image prints
  "∼20-fold"; the tilde is lost in the text layer. The value is approximate, so
  `cmp_rate_ratio` now gets no verdict (it was "close" before). The source notes still describe
  the earlier verdict.
- Added question `q_rate_ratio_approx` (p. 8) recording this change.
- Added question `q_fig2_wavelength_order` (p. 4): the caption says the wavelength increases from
  top to bottom, but the row 1 and row 2 q0 values (1.5, 2) give a shorter characteristic
  wavelength for row 2.

## Checked, no change

- Table 1 (p. 10): all 34 rows (l0, u, percent difference) match the image, including the signs of
  u = -1 that the text layer drops. The means come to 10.5% (spikes), 18% (holes) and 29.9%
  (stripes); `q_mean_spikes_holes` already records the mismatch with the printed 4.6% and 14%.
- Table 2 (p. 11): all -ln L, numbers of rates, qAB = 94.0 and qBA = 4.48 match.
- Table S4 (p. 29): 5.21, 23.7, 0.407; DOF 1, 5, 4; p values 0.05-0.01 and 0.99-0.95 match.
  The recomputed values (5.207, 23.65, 0.407; p = 0.022 and 0.98) agree.
- Family counts 205, 27, seven, 20, 178 (p. 7-8) match the image.
- `free_energy_eq6` matches Eq. 6 (p. 18), including the 3! and sqrt(K u4) factors, and
  u = u3 R / sqrt(K u4) (p. 19). Eq. 6 follows from Eqs. 3-4 by rescaling c; there is no
  inconsistency. Its settings T = 1, ΔT = 0.1 and R²τ/K = -1 match p. 19 (also in the Fig. 1
  caption, p. 3).
- `conserved_dynamics_eq7` matches Eq. 7 (p. 19); D = K = 1, u3 = -40, u4 = 120, R = 15, variance
  0.04, t = 2 (p. 4, p. 20) and τ = 20, -20, -20 and q0 = 1.5, 2, 0.5 by row (p. 4) match.
- `mode_number_wavelength`: l0 = 2πR/λ matches p. 18 and the Table 1 caption.
- Added inputs: none needed. The statistical models use only printed inputs. The likelihood-ratio
  form (2 Δ ln L) is a judgement of the first reader that is already a question (`q_lr_definition`);
  I agree with it.

## Not added (agreeing with the first reader)

- The 3-state test's p value "<<0.01" (p. 9, p. 29) is a bound and gets no verdict. chi2.sf(23.7, 5)
  ≈ 2.5e-4 is consistent with it.
- The Fig. 4 caption (p. 6) says chiral stripes occur at equilibrium when l0 is a half-integer and
  |u| ≪ 1. All nine stripe rows of Table 1 have half-integer l0, consistent with this rule. No
  printed number can be compared, so no comparison was added.
- The Fig. 4 boundary positions (l0 = 3.5-3.6, 4.5-5.5) and the Fig. 2 foams are figure geometry,
  left to the figure job.
