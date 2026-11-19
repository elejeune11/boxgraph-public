# Audit of stafford2004 (second reading)

Checked every datum in `data.yaml` against the page images (pp. 2-5), the three printed equations
against the images, the added inputs and the open questions. No transcription error was found.

## Checked, no change

- `nu_f_PS` 0.33 (p. 4), `Es_range` (1.5-2.0) ± 0.1 MPa (p. 4), `E_PS_gradient` 3.4 ± 0.1 GPa (p. 3,
  Fig. 2 caption), `E_PS_30nm` 3.4 ± 0.1 GPa (p. 4), `h_fig1b` ≈ 100 nm and `d_fig1b_text` ≈ 8 µm (p. 2),
  `d_fig1b_caption` 8 µm (p. 2, Fig. 1 caption), `nu_f_osg` 0.26 (p. 5), `porosity_range` "0 to 0.51
  percent" (p. 5), `E_osg_Pmax` 0.6 GPa (p. 4, Fig. 4 caption), `a_fit` 1 and `n_fit` 3.45 (p. 5),
  `allen_shortfall_printed` ≈10% (p. 3): all match the page images in digits, sign and unit.
- `wavelength_eq1` (Eq. 1, p. 2), `modulus_eq2` (Eq. 2, p. 2), `porosity_eq4` (Eq. 4, p. 5): the
  equations and code match the printed forms (symbols, the factor 3, the squared Poisson ratios, the
  exponents 1/3 and 3, (1 - aP)^n). Unit factors in the code checked by hand: Eq. 1 gives d ≈ 5.1 µm and
  Eq. 2 gives Ef ≈ 12.9 GPa for the Fig. 1b film, as `q_fig1b_inconsistent` says.
- `allen_shortfall` (reconstructed, p. 3): the reconstruction (plane-stress face on a half-space core
  of stiffness 2 Es q/((3 - nu_s)(1 + nu_s))) is Allen's standard face-wrinkling result; the ratio
  algebra checks, and gives 10.2% with nu_s = 0.5, nu_f = 0.33.
- `added.yaml`: `Es_added`, `nu_s_added`, `E0_added`, `P_max_added` each have a basis and real
  alternatives. No change.
- `references.yaml`: refs 1-16 checked against p. 5; no change.
- The scan of Fig. 2b (p. 3) supports `q_fig1b_inconsistent`: the open circles start near 8 µm at about
  150 nm thickness, not at 100 nm.

## Added

- `E_osg_P0` (p. 4, Fig. 4 caption): the printed 9 GPa at zero porosity, the other end of the range
  whose top is `E_osg_Pmax`. Not compared: `E0_added` is taken from it, so Eq. 4 at P = 0 would be circular.
  The validator's warning "never compared" on this datum is expected and left as it is.
- `h_PS_gradient_fig2a` (p. 3, Fig. 2 caption, 140-280 nm) and `h_PS_gradient_text` (p. 3, text,
  150-240 nm): the two printed thickness ranges of the PS gradient.
- `h_PS_plasticized` (p. 4, Fig. 3 caption, 110-130 nm) and `h_PS_indentation` (p. 4, ≈200-500 nm): the
  thicknesses of the two Fig. 3 series, which the figure pass needs as conditions.
- `h_osg` (p. 5, ≈725 nm) and `d_osg` (p. 5, "of the order of 30 µm"): recorded as data but not run.
  No modulus is printed for that film alone, so the first reader's choice to leave them out of the runs stands.
- `q_gradient_range` (reading, p. 3): the Fig. 2a caption range (140-280 nm, "doubling") differs from
  the text range (150-240 nm).
- `q_fig3_thickness_mismatch` (reading, p. 4): SIEBIMM and indentation in Fig. 3 are on films of
  different thickness. A consistency comparison of the two series must say so.

## Disagreements

- None that change a judgement. `cmp_eq4_Pmax` uses purpose `fit_quality` against a single end point
  whose E0 is an added value. I'd have weighed it lightly, as `q_eq4_endpoint` already says, so no
  separate question was added.
