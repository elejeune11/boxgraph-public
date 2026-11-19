# Audit of trujillo2008

Second, independent reading of `corpus/instabilities/2008_Trujillo.pdf` (PDF pages 1-6) against the
record, from the page images and text layer. Figures were not read (left to the figure job).

## Values checked (no transcription errors found)

- `lam_prod_biot` (p. 2): lambda1^2 lambda3 = 0.296, refs 20, 21: matches.
- `ec_biot_printed` (p. 2, repeated p. 4): e_c = 1 - lambda = 0.334: matches.
- `ec_mean_modulus_series` (p. 3, Fig. 3 caption p. 4): 0.33 ± 0.02, 200 um: matches.
- `ec_mean_thickness_series` (p. 4): 0.33 ± 0.01, 0.4 mol%, 3 um-1 mm: matches.
- `ec_southern_thomas` (p. 4): 0.349 ± 0.013, moduli of 1 MPa: matches.
- `poisson_ratio_gel` (p. 4): "~ 0.3" (tilde visible on the image): matches.
- `hh0_expected` (p. 5): h/h0 ≈ 2: matches.
- `hh0_onset_measured` (p. 5, Fig. 4 caption): 2.0 ± 0.1, h0 = 1.0 mm, 0.4 mol%: matches.
- `table1_modulus` (p. 2, Table 1): 0.05-2.0 mol% -> 0.6, 1.2, 2.4, 4.8, 8.4, 12, 24 kPa: all seven rows match.
- Citations: every quote was found on its page; printed page labels 564-569 match.

## Models checked

- `biot_equibiaxial` (p. 2): lambda1^2 lambda3 = 0.296 with lambda1 = lambda3 = lambda, e_c = 1 - lambda:
  matches the printed text; 1 - 0.296^(1/3) = 0.3336.
- `modulus_crosslinker` (p. 3): G = nu_x k_B T, "nearly proportional to the mole fraction of cross-linker";
  from words, prefactor unknown: matches.
- `thickness_from_strain` (p. 5): reconstructed (the paper gives no relation); a judgement of the first
  reader, left as is. Already questioned in `q_thickness_reconstruction`.

## Coverage and unstated inputs

- Every printed result the paper says comes from a model (0.334, h/h0 ≈ 2) is compared. The abstract and
  conclusion's "~0.33", "factor of ~2", "~0.6-24 kPa", "~1 MPa" restate recorded values and are approximate
  (no verdict); not added.
- No added inputs are needed: the reconstructed thickness model takes only printed values. No `added.yaml`.

## Changes made

- Added question `q_fig4_axis_label` (possible_error, p. 5): the top y tick label of Fig. 4 is printed
  "1.5" where the sequence 1.5 ... 2.2 implies 2.3; warning for the figure job.
- Added question `q_ec_trend_vs_mean` (reading, p. 4): the validation against the mean 0.33 ± 0.02 hides the
  slight upward trend of e_c with cross-linker content that the paper itself reports.

## Disagreements

- None with the first reader's judgements.
