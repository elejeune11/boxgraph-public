# Audit of cao2017 (second reading, 2026-11-21)

Scope: every printed number in `data.yaml` and every model against the page images (pp. 2, 3, 4, 5, 8, 9,
10, 11, 12). Figure values read by eye were not re-read; the next job digitizes the figures.

## Checked, no change needed

- Table S1 (p. 12): Ep, E_ECM_range, ki, En_range, K_cyto, rho0, beta_printed, alpha_printed, h_plaque,
  dmu0, dr_segment, phi0 (10^10 m^-2, OCR "1010"), rc, rECM: digits, exponents, units and sources match
  the page image.
- fiber_E, fiber_nu, fiber_r (p. 2): 140 MPa, 0.3, 1.8 um, as printed.
- oop_ratio (p. 8): 10^4 (OCR "104"), as printed.
- phi1d_low, phi1d_high, Lc_low_density, Lc_high_density (p. 9): 1 and 100 per um, 0.436 and 0.004 um, as
  printed.
- fiber_recruitment_eq1 (p. 2, Eq. 1): matches the printed form, factor 5 and erf[n(sigma - sigma_c)].
- steady_stress_eq4 (p. 3, Eq. 4): J = 2 pi D (sigma - Delta mu_0/Delta r) h (rc - rFA), sigma* =
  Delta mu_0/Delta r, as printed. Eq. 4 also follows from Eq. 3 as printed (checked by hand).
- contractility_s2 (p. 8, Eq. S2): matches the printed form. It also follows from Eq. S1 with sigma = rho +
  K eps, sigma = En eps_n = E*FA eps_FA and eps + eps_n + eps_FA = 0 (checked by hand).
- sigma_max_s2 (p. 8): beta rho0/(beta - alpha), as printed; the reduces_to relation rel_s2_to_sigma_max is
  stated on the page.
- shear_lag_length (p. 9): the printed Lc is (1/phi_i) sqrt[(1/kc)/(1/ks + 1/kp)], so Lc is proportional to
  1/phi_i with the stiffnesses fixed, as the model uses.
- coarse_grained_fa_ecm (p. 2, Eq. 2; SI pp. 8-9): governing equations and boundary conditions match.
- stable_size_chain, required_efa, normalize_fa_size: built from the printed equations and words; units
  checked (alpha, beta per Pa used per kPa; J/m^2 over nm = 10^6 kPa).
- added.yaml: alpha_per_Pa, beta_per_Pa, En_mid each have a basis and real alternatives.

## Changes

- Added model `keff_1d` (p. 9): the printed 1D effective stiffness keff(kp, ks, kc, L, phi_i) with the
  printed Lc, which the record did not hold. Not run: kp, ks, kc are not given. Tested directly: for small
  L/Lc it tends to kc phi_i L. New quantities plaque_stiffness_1d, ecm_stiffness_1d, clutch_stiffness_1d,
  fa_length_1d, effective_stiffness_1d.
- Added data `rFA_figS4`, `n_figS4` (p. 11): the parameters printed in the Fig. S4 legend (rFA = 8 um,
  n = 8), the conditions of that curve for the figure job.
- Added data `L_figS5F` (p. 9): the FA size 0.1 um at which Fig. S5F is computed.
- Added question `q_eq3_misreference` (p. 4, possible_error): the text cites Eq. 3 for the stiffness
  dependence of contractility, which is Eq. S2.
- Added question `q_keff_1d_unrun` (p. 9, unstated_input): how Fig. S5E/F can test the printed 1D formulas
  once digitized.

## Disagreements (no change made)

- source.yaml notes and q_En_range (pp. 8, 12) write computed numbers (sigma* = 1 kPa, Keff ~3.4 kPa, E*FA
  ~10.4 / 5.1 / 6.1 kPa). They are the first reader's explanation, not data, and are left; the build
  produces these values from run_sigma_star and run_Efa_required.
- No transcription errors were found in data.yaml or in the models.
