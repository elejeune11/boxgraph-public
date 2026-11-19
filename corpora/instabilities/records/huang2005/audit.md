# Audit of huang2005

Second reading of the paper against the record, from the page images (pp. 4-18). No figures were rendered or read.

## Checked, no change

- data.yaml: every value matches its page image: nu_film, nu_s_04, E_over_Es_3250, eps_c_3250_printed, lam_3250_printed (p. 12); eps_c_fig6_printed and the Fig. 6 panel strains used as the kbar_fig6 index (p. 11); kbar_fig6 values 1.000, 1.001, 1.002, 1.002 (p. 14); E_over_Es_325, lam_325_printed, eps_c_325_printed (p. 15); Ebar_over_Esbar_1e5, Nc_1e5_printed, lam_1e5_printed, kH_01, nu_s_04_p8, nu_s_05_p8 (p. 8); Ebar_over_Esbar_1000, nu_s_04_fig10, H_over_h_* (p. 16); nu_s_05_fig11 (p. 17). No transcription errors found.
- Models agree with the printed equations: g_eq10 (Eq. 10, p. 5), sinusoidal_finite_substrate (Eqs. 13, 16, pp. 5, 7), thick_substrate_eq17 (p. 7), thin_compressible_eq18 (p. 7), g_winkler_thin (p. 7), g_incompressible_thin and thin_incompressible_eq19 (p. 8), rms_stripes (p. 14), and the E_bar definitions in plane_strain_modulus_ratio (pp. 4, 5). By hand, Eqs. 18 and 19 follow from Eq. 13 with the stated thin limits of g, including their amplitude coefficients sqrt(2/3) and sqrt(1/2).
- spectral_patterns (Eqs. 21-27, p. 10): the summary in model.yaml matches the page. q_eq25_dimension is confirmed: Eq. 25 prints E_bar h^3.
- p. 8 claim that g rises by more than an order of magnitude from nu_s = 0.4 to 0.5 at kH = 0.1: Eq. 10 gives about 17.9 and 763, so the claim holds. The claim has no number, so it stays uncompared, as the first reader left it.

## Added

- g_thick_p7 (p. 7) and g_thick_fig3 (p. 6, Fig. 3 caption): the printed thick-substrate limit g(nu_s, infinity) = 1/2. The parser reads no fractions, so both are entered as "0.5", with a note that the page prints 1/2. They are compared through new runs run_g_thick_nu04 and run_g_thick_nu05 (g_eq10 at nu_s = 0.4 and 0.5, testing the claim that the limit does not depend on Poisson's ratio) and new comparisons cmp_g_thick_nu04, cmp_g_thick_nu05 and cmp_g_thick_fig3.
- kH_thick_added (added.yaml, p. 7): kH = 1000 stands for kH -> infinity, with alternatives 20 and 100. Eq. 10 is at 0.5 to double precision for all three.
- q_eqA1_symbol (possible_error, p. 17): Eqs. A.1 and A.2 both print "u" on the left side. The first is presumably the deflection w.

## Disagreements

- q_fig5_labels_overbar (reading, p. 9): the page image shows overbars on the Fig. 5 curve labels (E_bar/Es_bar = 10^3, 10^4, 10^5) and on the ordinate N_c/(E_bar h). The OCR drops them. q_fig5_modulus_ratio says the labels read E/Es. I left that question as it is and recorded this reading beside it.
