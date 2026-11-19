# Audit of moulton2012 (second reading, 2026-11-14)

Checked against the page images of pp. 4, 5 and 10 and the text of every page.

## Values (data.yaml)

- `kphi_fig5a` (15), `kphi_fig5b`, `K_fig5b`, `kphi_fig5c`, `K_fig5c` (1.2, 40), `rs0_fig5a` (0.8),
  `rs0_fig5bc` (0.7), `phi0_fig5` (0), `gamma0_fig5` / `gamma_rate_fig5` (gamma = 1 + 0.05t), `EA_fig5` (1),
  `ks_fig5` (5000), `kg_fig5` (2), p. 5, Fig. 5 caption: match the page image. No change.
- `a0_fig6` (1), `theta_fig6` (0), `EI_fig9` (0.1), `ks_fig9` (20), p. 10, Appendix F: match. No change.
- Figure data (`t_ribs_*`, `r_ribs_*`, `R_dashed_*`), p. 5: not re-read (figures are the next job's).

## Models

- `ribs_linear_eq4`, p. 4: Eqs. (2)-(4) as printed (dr_s/dt = k_g cos(theta) sin(phi); H1 = -k_phi n3). Matches.
- `ribs_tension_eq5`, p. 4: H2 = k_phi(1 - e^{K n3}) as printed. Matches.
- `ribs_decreasing_eq6`, p. 4: H3 = (k_phi/r_s)(1 - e^{K n3}) as printed. Matches.
- All three, p. 10: n3 from Eqs. (E.1)-(E.4), (1/a) n3 + k_s(a - r_s) = 0 with n3 = EA(a/(gamma a0) - 1),
  rearranged to k_s a^2 + (EA/(gamma a0) - k_s r_s) a - EA = 0; algebra checked. Matches.
- `mantle_unstressed_radius`, p. 10: gamma a0. Matches.
- `winkler_rod_wavelength` (reconstructed), p. 5: 2 pi (EI/k_s)^(1/4) is the standard straight-rod
  Winkler result for the energy of Eqs. (7)-(8). No change.

## Changes

- Added datum `L_excess_fig9` (L - L0 = 0.25, p. 10, Appendix F) with new quantity `mantle_length_excess`:
  a printed input of the bivalve model the record had left out. It feeds no model. Removed the phrase listing
  it as left out from `source.yaml` notes and added an audit line there.
- Added question `q_bivalve_strain` (reading, p. 6): the bivalve growth (L - L0) cannot be turned into an
  equivalent strain because the size of the initial semicircle is not given.

## Disagreements

- None with the first reader's judgements. Added inputs `a0_added`, `theta_added` have a basis and
  alternatives; `q_kphi_fig5a` (p. 5) is the right treatment of the panel (a) mismatch (value kept as printed).
- Reference `ref-fowler` gives the year as "1920": that is as printed on p. 11 (the paper is from 1992);
  left as printed.
