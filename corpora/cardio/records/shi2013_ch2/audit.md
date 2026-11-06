# Audit of shi2013_ch2

A second, independent reading of `corpus/cardio/2013_Shi_ch2.pdf` against the record. Every value
and equation was checked against the page images. Figures were not read: that is the next job's work.

## Values checked (no change)

- Table 2-1 (p. 20): CQao, CQmi, Elvs, Elvd, Plv0, Vlv0, Ela_max, Ela_min, Pla0, Vla0, CQpo, CQti,
  Ervs, Ervd, Prv0, Vrv0, Era_max, Era_min, Pra0, Vra0. All digits and units are as printed.
  Prv0 and Vrv0 are printed with the labels P_lv,0 and V_lv,0, and q_table21_labels already records this.
- Table 2-2 (p. 21): all 22 entries, including Vlv_init (500) and Vrv_init (400), are as printed.
- Annulus text (p. 21): d_annulus 25 mm, h_annulus 1 mm, rho_tissue "0.8 x 10^3" kg/m^3,
  A_annulus_text "4.7 x 10^-4" m^2 and m_annulus_text "4.0 x 10^-4" kg. The exponents are right on the
  image.
- Table 2-3 (p. 22): all 12 entries are as printed (units m/(s^2 mmHg), 1/s, 1/s^2, kg, m^2).
- Table 2-4 (p. 23): the 8 K_p and K_f values are as printed. Table 2-5 (p. 23): T, Ts1, Ts2, Tpwb
  and Tpww are data, and dt = 0.0001 s is the model setting dt. theta_closed is on p. 17.
- Results on pp. 26, 27, 28, 34, 35, 36, 41 and 47: every predicted value matches the image
  (digits, sign of -0.0286 m, units ml, ml/s, mmHg, m).

## Models checked (no change)

- circulation_ch2 against Eqs. 2-1 to 2-6 (pp. 12-14), 2-7 to 2-12 (pp. 15-16), 2-13 to 2-15 (p. 17),
  2-17 (p. 18) and 2-18 to 2-23 (p. 19). Every equation in the code has the printed form:
  - the activation branches and their intervals;
  - the KG force balance with M_sav on the left and the sign convention (into the atrium is positive,
    p. 15);
  - Eq. 2-13 as printed, with no minus sign on the reverse branch;
  - AR = (1 - cos theta)^2/(1 - cos theta_max)^2;
  - leaflet dynamics K_p dP cos theta - K_f dtheta/dt;
  - total resistance R_sat + R_sar + R_scp in Eq. 2-21.
  The printed model is not a corrected one.
- circulation_ch2_signed: only the sign on the reverse branch of Eq. 2-13 differs. It is a variant
  (`variant_of`) with its evidence, beside the printed model.
- annulus_geometry and annulus_mass (p. 21, from words): A = pi d^2/4 and m = rho A h are a fair
  reading. q_annulus_area records the misfit (4.9 vs 4.7 x 10^-4 m^2).

## Unstated inputs (no change)

- theta_max_added, Vla_init_added, Vra_init_added, Psas_init_added, Psat_init_added,
  Psvn_init_added, Ppas_init_added, Ppat_init_added and Ppvn_init_added (p. 22) each have a basis
  and alternatives. q_initial_values and q_theta_max say why they are needed.

## Printed results

- Every predicted datum in data.yaml has a reproduction comparison. The simplified-model values printed
  twice have consistency comparisons. I found no exact model result that is printed but not compared.
- Not recorded, approximate: on p. 43 (printed p. 91), valve dynamics stretch the KG diaphragm
  "about 0.002 ~ 0.004m" further in systole. The notes' list of left-out approximate values does not
  name it. Added to q_audit_kg_measurements.

## Changes and disagreements

- Added question q_audit_kg_measurements (kind `reading`, pp. 8, 21, 22, 43). It disagrees with the
  first reader's choice to leave out the MRI measurements of KG diaphragm motion: 0.02-0.03 m per
  cycle (p. 8), about 0.003 m into the atrium in diastole (p. 22) and 8-12 ml of volume (p. 8). They
  are the measurements the KG model should be validated against. The question also notes the
  approximate p. 43 result, and that A_sav x 0.02-0.03 m = 9.4-14.1 ml does not quite match 8-12 ml.
  No datum was added: the scope is the first reader's call.
- No transcription error found. No datum, model, run or comparison was changed.

The validator reports SOUND after the audit.
