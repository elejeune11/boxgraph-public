# Audit of panzetta2019 (second reading, 2026-11-21)

Scope: data, models, added inputs and questions checked against the page images (pp. 6-9, 23, 24) and
text. Figures were not rendered or re-read; that is the next job's work.

## Values (data.yaml)
- No printed numbers to check: every datum (figS13l_flow, figS13r_*_flow, fig9r_*_flow, fig9r_*_flow_at_s13,
  fig9l_*_flow) is a figure datum. Axis quantities and units (Actin flowrate [nm/s]; Substrate spring constant
  [pN/nm], linear in Fig. 9 right p. 8 and log in Fig. S13 p. 23; Number of clutches, Fig. 9 left) match the
  pages. Citations and pages are correct. No change.

## Models (checked symbol by symbol against the page images)
- clutch_two_spring_cycle (p. 9): Eqs. 3, 4, 5, 6, 7, 8, 10, 11, 12 are transcribed as printed in model.yaml.
  model.py: Fs - F0 = ks[2(xs - x0) - l(xs/sqrt(l^2+xs^2) - x0/sqrt(l^2+x0^2))] agrees with Eqs. 6-7 and the
  bracket of Eq. 10. dFs/dxs = ks(2 - l^3/(l^2+xs^2)^(3/2)) is correct from Eq. 7. dxs/dt = Pb vf/(Pb + Fs'/(nc kc))
  follows from Eq. 12 with Eq. 8 (<xc> = xs + (Fs - F0)/(nc kc)). The (r Pb Fb/(r Pb Fb - <Fc>))^r form equals
  the (1 - <Fc>/(r Pb Fb))^-r of Eq. 11. No change.
- clutch_canonical_cycle (p. 24): s.1-s.6 transcribed as printed. <Fc> = kc ks/(ks + nc kc)(<xc> - x0) follows from
  Eq. 4 and s.4. s.5 and s.6 match the image, and s.6 follows from Eq. 12 with s.4. No change.
- q_eq13 checked: Eq. 13 on p. 9 has dxs/dt on both sides ("/(1 - Pb) dxs/dt + Pb vf"), as the first reader says. Agree.

## Added inputs (added.yaml)
- All 15 added inputs have a basis and alternatives. The paper states no input (q_params_unstated confirmed:
  pp. 6-9, 24 give none). No disagreement on the choices.

## Questions
- Added q_eq_crossrefs (possible_error, p. 9 and p. 24): "Eq. 7 becomes" (should be Eq. 9), "Combining Eqs.
  3-5" (Eq. 8 uses Eqs. 4-7), and "the Hill equation" for the linear Eq. 9. These do not affect any model.
- Added q_fig9_vs_S13_direction (reading, pp. 8, 23): a disagreement with q_fig9_vs_S13's wording that Fig. 9
  (right) rises more slowly towards stiff substrates than Fig. S13 (right). By eye, Fig. 9 reaches 40-60 nm/s at
  80-100 pN/nm, whereas Fig. S13 stays below 22 nm/s. q_fig9_vs_S13 itself is left unchanged.
- Checked q_fig9_panels (p. 7 text against the p. 8 legend), q_figS13_caption and q_eq11_ref (ref. 39 is Dupont et
  al., YAP/TAZ): all confirmed.

## Coverage of printed results
- The paper's model results are only the curves of Figs. 9 and S13, and all ten are compared. Fig. S13 also plots
  points below 5 pN/nm (near 1 pN/nm in both panels and 0.1 pN/nm in the right one), but the readings start at
  5 pN/nm. This is a matter for the figure job, which may extend the `at` lists. Not changed here.
- No further printed model result (no number, no optimum value) was found in the text.

## Changes made
- questions.yaml: two questions added (above). Nothing else changed.
