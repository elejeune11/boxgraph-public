# Figures of qiu2022

- **Fig. 1** (p. 1): photographs of a buckled straw, balloon and E. coli cell, and a geometry sketch. No values: left out.
- **Fig. 2(a)** (p. 4), shell normalization, and **Fig. 2(b)**, balloon normalization: each panel holds five
  pressures (curve labels p-bar = 0, 2.5, 5, 7.5, 10 and p-hat = 0.02, 0.05, 0.1, 0.2, 0.4), each drawn as a
  solid line (numerical minimization of Eq. 2) and a dashed line (Eq. 8), with a dot (numerical wrinkling
  onset) and a black cross (Eq. 11) on each. All are read by code (figures/_fig2.py; one file per reading):
  the 20 curves at chosen curvatures where each line can be told apart (below kappa-bar ≈ 1.4 and
  kappa-hat ≈ 0.07 the five pressures lie on top of one another and are not read; where a dashed line
  coincides with its solid line the joint ink is read for both), and the 10 dots and 10 crosses as the
  curvature at which they sit, indexed by the pressure label of their curve (matched by colour). Each reading
  was checked on an overlay.
- **Fig. 2(a) and 2(b), shared trunk** (second pass): the low-curvature stretch where all ten lines of a
  panel form one band of ink, read by figures/fig2_trunk.py as readings `rd_fig2a_trunk` (kappa-bar = 0.4 to
  0.8) and `rd_fig2b_trunk` (kappa-hat = 0.01, 0.03, 0.04, 0.05). Calibrated as the other Fig. 2 readings
  (ticks matched to the printed labels, the calibration misfit added to the interval). The code reads a
  position only when the coloured ink in a 7-px column window is one connected band. The value is the band's
  middle. The interval is the whole band plus the misfit, so it spans the five pressures. Positions where the
  lines already separate (kappa-bar ≥ 0.9, kappa-hat ≥ 0.07) are dropped. So are kappa-hat = 0.02 and 0.06,
  where a coloured wrinkling dot sits on the band and would widen it. Data `fig2a_trunk` and `fig2b_trunk` are
  compared with Eq. 8 at the lowest and highest pressure of each panel (p-bar = 0 and 10; p-hat = 0.02 and
  0.4, alpha = 0.005). Both pressures fall inside the band at every position read.
- No figure in this paper plots measurements: Fig. 2 holds only model curves and computed onsets, and the
  experiments the text mentions (osmotic-shock buckling, ref. 20) are not plotted. So there are no
  measured data or error bars to read. No figure settles an open question beyond what the first pass
  recorded (q_fig2b_alpha).
