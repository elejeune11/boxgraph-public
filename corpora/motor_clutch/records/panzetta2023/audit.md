# Audit of panzetta2023

Second reading of `corpus/motor_clutch/2023_Panzetta_with_SI.pdf` (PDF pp. 1-13) against the record,
from the page text and page images (figures not read: that is the next job).

## Checked, no change

- Table 1 (p. 3): `Fm_t1` 2 pN, `vu_t1` 120 nm/s, `Fb_t1` 2 pN, `kon_t1` 0.3 s^-1, `koff_t1` 0.1 s^-1,
  `kc_t1` 0.8 pN/nm: all as on the page image.
- `ks_soft` 0.1, `ks_stiff` 1 pN/nm, `ke_soft`/`ke_stiff` (ks^eps0 = ks), grids 25 values 10-200 and
  20 values 10-1000 (p. 3): as printed.
- Strains `eps_0`, `eps_01`, `eps_3` (p. 5), `eps_025`, `eps_05`, `eps_1`, `eps_1_s3`, `ldef_s3`,
  `l_ortho` 1000 nm (p. 7): as printed.
- `ldef_eps3_printed` 4000, `ldef_eps0_printed` 1000, `lrest_s3_printed` 500, `ldef_eps1_s3_printed`
  2000 (p. 7): as printed.
- `ncopt_soft_0_printed` 40, `ncopt_stiff_0_printed` 445, `ratio_stiff_soft_printed` 10,
  `inc_soft_01_printed` 3, `inc_soft_3_printed` 103, `inc_stiff_01_printed` 3, `inc_stiff_3_printed` 69
  (p. 6, image), `inc_tr_025/05/1_printed` 64/71/76 (p. 7, image), `dn_soft_01_printed` 1 (p. 9),
  `nc_50`/`nc_400` (p. 4): as printed.
- Models against the page images: Eq. 1 (p. 2) in `strain_eq1`/`strain_eq1_inverse`; Eqs. 2-6, 10-12
  (p. 3) in `clutch_axial_ssa`. Eq. 6 prints l' (the deformed length, Eq. 1) inside both square roots
  and l outside; the OCR's "l0 2" is that l'. The model's L = l (1 + eps0) is that l', so the model is
  the equation as printed. Eqs. 7-9 in `clutch_transverse_ssa` with F0 as printed (Eq. 8); the
  reader's readings of Fs and the motor load are recorded in q_transverse_fs / q_transverse_load.
- No `added.yaml`: every input of every run is printed; the unstated choices (time average, spline in
  log nc, events and seeds) are settings recorded as questions (q_average, q_spline, q_events).

## Changes

- `ldef_eps1_s3_printed` (p. 7; Fig. S3 caption p. 13): the note said the 2000 nm deformed length is
  "Fig. S3, solid line"; the caption gives 1000 nm for the solid line and 2000 nm for the dashed line.
  Note corrected to "dashed line". Value unchanged.
- Added model `increase_from_percent`, run `run_dn_soft_01_printed` and comparison
  `cmp_dn_soft_01_printed` (consistency, pp. 6 and 9): the printed "+1 clutch" at strain 0.1 on the
  soft substrate against 3 % of the printed optimum 40 (= 1.2).
- Added question `q_s3_caption` (possible_error, p. 13): the Fig. S3 caption calls 1000 and 2000 nm the
  "initial" length; the text (p. 7) makes them the deformed lengths, with an initial length of 500 nm.
- Added question `q_fig9_caption` (possible_error, p. 8): the Fig. 9 caption announces 7 strain levels
  but lists six (0.1 missing); the axes show seven.

## Disagreements and remarks (no change)

- None with the first reader's judgements. Two remarks for the figure job: Fig. 4A (l = 100 nm, p. 6)
  is the only evidence for the claim that a short orthogonal spring shifts the optimum up (p. 5), and
  Fig. 6 read with the caption's colours (grey = 0.1 pN/nm on the left axis, black = 1 pN/nm on the
  right axis), looked at by eye only, ends near 81 and 740, consistent with the printed +103 % and +69 %.
