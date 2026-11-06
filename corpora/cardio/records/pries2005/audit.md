# Audit of pries2005

Second, independent reading against the page images (PDF pp. 1-8). Figures were not read (left to the next job).

## Checked, no change

- data.yaml: every printed value checked against the page images: fitted parameters Doff 2.4, Dcrit 10.5, D50 100, Eamp 1.1, Ewidth 0.03, Epeak 0.6, EHD 1.18 and the EHD = 0 set (Eamp 1.23) (p. 3); Wmax 2.6 (p. 2); 40%, ~1 mm, ~3.2, ~1.25, 6-7 um, minimum at 6-7 um (p. 1); minimum at 5-7 um (p. 2); 10.5 um peak (p. 3); ~0.8-1 um for 10- to 40-um vessels (p. 1); ~30-50 um (p. 5); 7 to 9 um, ~0.5-0.7 um, 8-10.4 um (p. 6); 4.2 cP, ~30 um, ~1.5 cP, ~3.4 um, ~720 ml, ~350 m^2, 2 um (p. 7). All digits, signs, units and pages agree; no exponent errors.
- Models: vitro_viscosity (Eqs. 5-7, p. 2), esl_thickness (Eqs. 8-11, pp. 2-3), vivo_viscosity (eta_vivo = eta_vitro(Dph)(D/Deff)^4, p. 3), fahraeus_vitro (Eq. 12, p. 3) and fahraeus_vivo (Eq. 13 as printed, (D/Dph)^2, p. 3) match the printed equations in symbols, signs and factors. fahraeus_vivo_core is correctly kept as a variant beside the printed Eq. 13. The Discussion arithmetic models (anatomic_diameter, esl_from_viscosity, esl_from_volume, p. 6-7) follow the text.
- Hand check of the runs: Wph(10 um) = 0.81 um and Wph(40 um) = 0.99 um at the fitted parameters; Lipowsky layer 3.40 um; Rehm layer 2.06 um; 7 + 2(0.5) = 8 and 9 + 2(0.7) = 10.4 um.
- added.yaml: HD_vitro_minimum, HD_figure and D_tube_10 each have a basis and real alternatives.
- Open questions q_eq13_factor (p. 3), q_eq14_ratio (p. 3) and q_intro_hd40 (p. 1) checked: independent arithmetic agrees (Eq. 13 as printed gives HT/HD about 1.03 at 10 um, HD 0.45; eta_0.45 at 6.5 um is 1.25, so the introduction's values are those of HD 45%).

## Changes

- `eta_small_tube_printed` (p. 1): citation quote "to only" (two words, not locating the value) replaced by the consecutive words "in tubes with diameters above 1 mm to only 1.25 in" from text/page-001.txt. Value unchanged.
- `Dpeak_abstract` (p. 1): new datum, the abstract's "a maximum for ~10-um-diameter vessels" (printed "~10", origin predicted), a printed model result not yet in the record.
- `cmp_weff_peak_abstract` (p. 1): new consistency comparison of Dpeak_pred with Dpeak_abstract (tilde: no verdict expected, recorded for completeness).

## Disagreements and notes

- None with the first reader's judgements (added values, choices, model scope).
- source.yaml `reader.model` is `None`; left as is, since the first reader's model id is not known to this audit.
