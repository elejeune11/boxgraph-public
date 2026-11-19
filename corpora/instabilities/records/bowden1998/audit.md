# Audit of bowden1998 (second reading, 2026-11-13)

Checked against the page images (PDF pp. 1-4); no figures were rendered or read.

## Values checked, no change
- Em_gold 82 GPa, Ep_pdms 20 MPa, nu_m_gold 0.33, nu_p_pdms 0.48 (p. 3): match the page.
- t_gold 50 nm, t_adhesion 5 nm (p. 1; also Fig. 1 and Fig. 2 captions, p. 2): match.
- L_measured "20 to 50" um, depth_unheated 1.5 um, depth_300C 3.9 um at 300 degC (p. 2): match; the OCR "mm" is um on the page.
- L_over_t_eq3_printed "≈ 61", L_estimate_eq3 "~3.4" um (p. 3): match.
- l_over_t_eq5_printed "≈ 1060" (printed 1,060t), l_over_L_printed "17" (p. 4): match.
- t1_modified 2 um, E1_modified "≈ 80" MPa, factor_modified_printed "7" (p. 3): match.

## Models checked, no change
- thermal_stress_eq1 (p. 3, Eq. 1): sigma_o = Em(alpha_p - alpha_m)(T_D - T)/(1 - nu_m), as printed.
- critical_stress_eq2 (p. 3, Eq. 2): 0.52 (Em/(1-nu_m^2))^(1/3) (Ep/(1-nu_p^2))^(2/3), as printed.
- wavelength_eq3, wavelength_eq3_simplified (p. 3, Eq. 3): 4.36t[...]^(1/3) and 4.4t(Em/Ep)^(1/3), as printed.
- transition_length_eq5, transition_length_eq5_simplified (p. 4, Eq. 5): 0.3t[...] and 0.3t(Em/Ep), as printed.
- transition_to_wavelength_ratio(_simplified): ratios of the forms above, as printed.
- multilayer_wavelength: marked reconstructed; its scope is the first reader's judgement, not changed.

## Coverage
- Every printed result that comes from a model is compared (61t, 3.4 um, 1,060t, 17, factor of 7) and so is the
  paper's comparison with the measured wavelengths. Eqs. 4a, 4b, 6a and 6b give no printed numbers. The
  "≈ 20" ratio alpha_p/alpha_m (p. 3) feeds only Eq. 1, which cannot be run (q_eq1_inputs), so I did not add it
  as a datum.

## Changes
- No transcription errors found; no datum, model, run or comparison changed.
- Added question q_t_fig3_inset (reading, p. 3): the Fig. 3 inset labels the layer of thickness t "Au/Ti",
  which supports t = 55 nm over the added 50 nm (t_film_added); the first reader's choice is kept.
- Added question q_depth_no_model (unstated_model, p. 2): the measured depths have no model or strain in the
  paper, so they are not compared.

## Validator
- SOUND; one warning left on purpose: thermal_stress_eq1 is never run (q_eq1_inputs).
