# Audit of jin2015

Second, independent reading against the page images (pp. 1-11). Figures were not rendered or read.

## Values checked, no change

- All values in `data.yaml` checked against the page images: `e_crease_pe`, `e_crease_uni` (p. 6); `boundary_Gf_Gs` 1.65 (p. 3, text and Fig. 3(a)); the twelve Fig. 3(a) contour labels 0.01/0.008, 0.02/0.015, 0.05/0.038, 0.13/0.1, 0.25/0.19, 0.44/0.35 (p. 3); `eF_compliant_layer` 0.36 (p. 4, Fig. 4 caption); `em_biot_uni` 0.556 (p. 10); `mounting_G` 260 kPa, `mounting_H` 1 mm, `substrate_H_exp` ≈ 550 um, `film_H_exp` 18 to 20 um (p. 7); the experimental strains 0.37, 0.28, 0.29, 0.22 to 0.28, 0.18 to 0.21, 0.21 (p. 7) and 0.36, 0.28, 0.22, 0.18 (p. 10). No transcription error found.
- `source.yaml`: authors are Jin, Auguste, Hayward and Suo (p. 1). The batch description names "Holmes" as the last author; the page shows Zhigang Suo, so the record is right.

## Models checked, no change

- `wrinkle_eigen_plane_strain` / `wrinkle_eigen_uniaxial` (p. 10, Eqs. B8-B15): every entry of the 8 x 8 matrix checked against the page image, including the signs the OCR drops (A12, A32, A34, A35, A37, A45-A48, A51, A53, A57, A58 and the "A5j = -A5(j+4)", "A6j = -A6(j+4)" pairs) and the exponents KHf/(lambda1^2 lambda3), KHf, K(Hf+Hs)/(lambda1^2 lambda3), K(Hf+Hs). The code matches the printed matrix; uniaxial lambda3 = 1/sqrt(lambda1) (p. 9) and e_c = 1 - lambda_c (p. 10) match.
- `eq1_wrinkle_uniaxial_to_plane`, `eq1_crease_uniaxial_to_plane` (p. 3, Eq. 1): 1 - e^PE = sqrt(lambda3)(1 - e) as printed.
- `equal_strain_boundary_plane_strain`, `equal_strain_boundary_uniaxial` (p. 3): match the text's definition of the boundary.

## Additions

- data `Gf_Gs_pointA` ... `Hs_Hf_pointF` (p. 6): the moduli and thickness ratios of points A-F (1.4/0.2, 1.4/2, 2.5/9, 3/9, 3.5/9, 5/49), printed in the text and in Figs. 5(a)-(f). They were not in the record.
- runs `run_em_pe_pointA` ... `run_em_pe_pointF` (p. 6, Fig. 5): e_m^PE and L_m/Hf at points A-F from `wrinkle_eigen_plane_strain`, ready for comparison with the diamonds of Figs. 5(a)-(f) once a figure pass reads them. `figures.md` updated to say so, and to list Figs. 4(a)/5(g) (the boundary curve) for the figure pass.
- comparison `cmp_Lm_independent_of_loading` (p. 3): the paper states that K_m, and so L^m_wrinkle/Hf, does not depend on lambda3 (text below Eq. 1, Fig. 3(b) caption); compares the uniaxial and plane strain L_m at the boundary point.
- question `q_points_AF_diamonds` (p. 6), kind reading: the classification of points A-F by the wrinkle analysis is only checkable through the Fig. 5 diamonds.

## Disagreements with the first reading

- None on values, models or added inputs. `Hs_Hf_thin_film_limit` (added 1000, alternatives 10, 100, 10000) and `Hs_Hf_homogeneous` have a basis and real alternatives. `q_boundary_165` (p. 3) stands: the printed matrix puts the thin-film boundary below 1.65, so this is a finding and not a reading error. The same matrix gives the Biot strains for one layer in both loadings.
- Not added: the Fig. 3(b) contour labels L^m/Hf = 5, 11, 16, 25, 40 (p. 3). Their positions need a figure reading, so they are left to the figure pass already listed in `figures.md`.
