# Audit of haas2015 (second reading)

Checked against the page images (pages 1-12) without rendering the PDF or reading figures.

## Changes

- `phi_eq29` (p. 3, Eq. 2.9): the equation was written with the symbol Phi; the page prints an
  italic F (`F = r(1)`, Fig. 2(b, c), Eq. 2.9). Equation string corrected to `F = (1/2)[(1 - nu) + (1 + nu) f]`;
  the output port keeps the name `Phi` (runs refer to it) and its description now says it is the printed F.
- `lame_plane_numeric` (p. 3, Eq. 2.5): `Phi = r(1)` in the equation string corrected to `F = r(1)`.
- `contracted_boundary_radius` (quantities.yaml, p. 3): name said `Phi = r(1)`; corrected to `F = r(1)`.
- `q_lambda_max_pi2` (p. 8): new open question (kind `reading`): lambda_max = pi R/2 (Fig. 8 label
  and text) is not recorded as a datum because it is printed as a multiple of pi; it should be
  carried to the comparison with haas2021.

## Checked and agreeing

- Data: `nu_computations` 1/2 and `h_over_R_computations` 0.15 (p. 3), `lambda_max_fig5` 1.1 and
  `rp_fig5` r_p = R (p. 6, Fig. 5 caption), `rp_fig8_least` 0.75 (p. 8, Fig. 8 colour bar),
  `L_min_fig3g` 2.44 (p. 4, tick label of Fig. 3(g)), `L_min_text` approx 2.44 (p. 5). Digits, pages
  and quotes agree with the page images.
- Models: `phi_eq29` (Eq. 2.9; also derived independently from (2.5)/(2.7)/(2.8): the stress
  continuity and the jump condition of (2.7) both give (2.9)); `curvature_eq33` (Eq. 3.3 = B15);
  `rotation_b18` (Eq. B18, numerator and denominator term by term); `rotation_contraction_eq35`
  (Eq. 3.5, 1/(2 sqrt2)); `curvature_b14_numeric` follows (B14) as printed; `rotation_b16_numeric`
  follows (B8) and (B16) as printed; `shell_bifurcation` (Eq. 2.4) agrees.
- The scalings agree between the main text and Appendix B: delta ~ (h/R)^1/2 (p. 5) with
  delta = eps^1/2, eps^2 = h^2/(12(1 - nu^2) R^2) (B2, p. 9); k = d^1/2 delta^-3/2 K (3.3) and
  k = d^1/2 eps^-3/4 K (B6); d/delta in (3.4) and d/eps^1/2 in (B17). The scaling laws (3.7) agree
  with (C3)-(C7) once the prefactors are dropped. No question needed.
- The sign question `q_b14_sign` (B8 against B14, p. 10) is confirmed: from (B8),
  b0'''' + b0 = -K0'', the opposite of the printed (B14).
- Unstated inputs: `f_probe_added` and `L_probe_added` are refinement probes feeding no
  comparison, each with alternatives. The numerical settings of the reconstructed models are
  stated in the run notes. Nothing missing.
- Printed results not yet compared: none with a value. The paper's other results (Figs. 5, 7, 8,
  the critical point (lambda*, k*)) come from the shell computation that is not rerun
  (`q_shell_not_rerun`) and print no number. Fig. 2 scale bars (50 um, 20 um, p. 2) are not model
  inputs. The paper makes no quantitative comparison with measured embryo shapes.

## Disagreements

- None with the first reader's judgements. Applying nu = 1/2 to the plane test case of Fig. 2(c)
  follows the paper's "In computations, we take ... nu = 1/2" and is reasonable.
