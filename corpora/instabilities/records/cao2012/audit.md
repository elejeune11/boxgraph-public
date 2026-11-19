# Audit: cao2012

Second, independent reading of the record against the page images (pp. 1-9). No figures were read.

## Checked, no change

- `data.yaml`: every printed value checked against the page image. The modulus ratios 5, 30 (pp. 5-6), 186
  (p. 6) and 836 (p. 7), the prestretches 1.3 and 2 (p. 6), the constant 0.5437 of Eq. 7 (p. 4), the
  homogeneous limits 0.456 (p. 2) and 0.556 (p. 4; also the labelled tick of Fig. 7), the caption strains
  ≈ 0.055 (Fig. 9, p. 5), ≈ 0.175 (Fig. 10, p. 6), 0.019 and 0.314 (Fig. 12, p. 6), ≈ 0.01 and 0.0367
  (Fig. 14, p. 7) and ePD ≈ 0.2 (p. 5) all match, with the "≈" kept where printed. No transcription error found.
- `simple_formula_plane` (Eq. 5, p. 2) and `simple_formula_uniaxial` (Eq. 6, p. 4): prefactors 1/4 and 1/3,
  exponents 2/3 and 1/3, and Lambda as printed. Both also agree with the general Lambda of Eq. 2 with
  lambda0_3s = 1 and lambda0_3s = 1/sqrt(lambda0_1s).
- `biot_surface_eq7`, `biot_surface_eq7_uniaxial` (Eq. 7, p. 4): as printed, eW = 1 - 0.5437/sqrt(lambda_3).
- `bilayer_plane_strain`, `bilayer_uniaxial` (Eqs. A1-A10, pp. 7-8): A, B, C, D and E checked term by term
  against the page images. I re-derived A3-A5 and D (A9) from A1-A2. I also re-derived the factor
  (1/lambda0_3s)(mu_s/mu_f) of A10 from A7 with k_bar = lambda0_1s k. All agree with the printed forms and
  with the code. The stretch states (Eqs. 1, 3, Sec. 3.3) are also right.
- `added.yaml`: the record has no added inputs. The numerical scheme of the exact analysis is the
  reader's choice and is recorded in q_numerical_scheme. I agree that no physical input is unstated.

## Changes

- Added datum `eW_interface_footnote2` (p. 2, footnote 2). The paper states that 0.456 is also the
  critical strain for interface wrinkling between two bonded neo-Hookean half-spaces. Added comparison
  `cmp_eq7_interface` (consistency) against the existing Eq. 7 plane strain run.
- Added question `q_audit_ridge_twice_eW` (overstated_claim, p. 6). The Fig. 13 caption says ridges
  form at "roughly twice eW", but Fig. 14 (p. 7) prints eW ≈ 0.01 and a first ridge at 0.0367, about 3.7 times.
- Added question `q_audit_fig9_snapshot` (reading, pp. 5-6). The first snapshot of Fig. 9 is
  labelled e = 0.055, the caption's bifurcation strain. Sec. 4.1 says the FE "buckle" analysis gives
  eW directly. This supports the first reader's hypothesis in q_eW_ratio30_ratio5 that the caption
  values are finite element values. It also points to Fig. 8 as a second curve to read.

## Disagreements and remarks (no change made)

- `simple_formula_uniaxial` is never run. The paper prints no number from Eq. 6, so this is correct. Fig. 7
  (the e0 curves) is where the figure pass can test it.
- The post-bifurcation strains (`ePD_*`, `eMR_*`) stay uncompared against the non-runnable
  `fe_postbifurcation`. I agree with this; it is covered by q_fe_not_runnable.
- The first reader left out the crease threshold e = 0.35 (p. 2, from Refs. 6-7) and the snapshot strains
  that mark no onset. I agree with both choices.
