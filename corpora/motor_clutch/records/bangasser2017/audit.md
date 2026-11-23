# Audit of bangasser2017 (second reading, 2026-11-19)

Second reader: boxgraph auditor (agent). Checked against the page images of PDF pp. 2-8, 12, 21 and
the page text of pp. 2-6. No figures were rendered or read (that is the next job).

## Values checked, no change

- All 23 Supplementary Table 2 data (`Nm_low` ... `Fb`, p. 12) agree with the page image: digits,
  units, and the exponents of `kmod_star`, `kcap`, `kon`, `koff_star` (s^-1).
- Fig. 1 legend data (`Nm_low_fig1` ... `ks_rmcpeak_high_fig1f`, p. 3) agree with the page; the
  OCR's "B" is the page's "~" throughout.
- `dK_opt_fig1g` (p. 3, "4-fold") and `dEopt_fig4f` (p. 6, "2-fold") agree with the panels.
- Supplementary Fig. 5 data (`t_steady_suppfig5`, `Nm_suppfig5`, `nm_star_suppfig5`, `ks_suppfig5`,
  p. 21) agree with the page.
- `n_init_modules` (p. 7, "three") agrees.
- Gel and PIV data (`V_gel_thin` ... `L_lattice`, p. 8) agree with the page image (µl, µm, which the
  OCR reads as ml, mm).
- `Eopt_u251_text`, `Eopt_treated_text`, `Eopt_ecfn_text` (p. 5) agree with the text.

## Models checked, no change

- `off_rate_eq1` (Eq. 1), `motor_velocity_eq2` (Eq. 2), `polymerization_eq3` (Eq. 3),
  `module_birth_eq7` (Eq. 7, fourth power), `module_motors_eq8` (Eq. 8), `module_clutches_eq9`
  (Eq. 9), `rmc_eq12` (Eq. 12) match the equations as printed on p. 7. `module_ssa` uses Eqs. 1, 2,
  4, 10, 11 as printed. Eq. 10's lower limit "i = i" is confirmed on the image (`q_eq10_index`).
- `cms` settings (15 min sampling, first hour discarded) match p. 7.
- `added.yaml` (`pixel_size_40x`, `nm_free_full_low`, `nc_free_full_low`) each have a basis and
  alternatives.

## Additions

- Added quantities `cell_type_optimal_modulus` and `cell_type_optimum_fold`.
- Added data `Eopt_ecfn_p3` (~1 kPa), `Eopt_u251_p3` (~100 kPa), `optimum_fold_p3` (~100-fold),
  p. 3: the cell-type optima behind the paper's "~100-fold more motors and clutches" claim; they were
  not recorded.
- Added model `cell_type_optimum_fold`, run `run_celltype_fold_p3`, comparison
  `cmp_celltype_fold_p3` (consistency; all values approximate, so no verdict).
- Added question `q_fig4b_traction_drop` (p. 6 legend "approximately fourfold on all stiffnesses"
  against p. 5 text "about an order of magnitude" at 9.3 kPa).
- Added question `q_u251_flow_min_range` (p. 3 text "between 20 and 100 kPa" against Fig. 3c legend,
  p. 5, "between 9 and 200 kPa").
- Added question `q_fig4f_p` (p. 6: panel "P <0.015", legend "P = 0.015"), as `q_fig1g_p` for Fig. 1g.
- Added question `q_shift_proportionality` (pp. 3-4): the text applies a proportional
  optimum-to-motor-clutch-number rule (100-fold) that the simulator shows only for the flow minimum
  over a tenfold change (Fig. 1g composite: 4-fold; Fig. 1d traction: no shift).

## Disagreements (recorded as questions, nothing changed)

- `ks_flowmin_low_fig1c` (p. 3), `Eopt_u251_text`, `Eopt_treated_text`, `Eopt_ecfn_text` (p. 5): the
  page prints these with words ("around", "near"), not with "~"; the first reader entered "~". Kept as
  a judgement; question `q_approx_signs` (kind reading).

## Not added, and why

- Measured and simulated values only plotted (Figs. 1c-g, 2-4, S2, S4, S5) are left to the figure pass.
- Supplementary Fig. 5 per-substrate simulation counts (40, 34, 15; p. 21), the Fig. 3b kymograph label
  "79.5 nm s-1" (p. 5) and the "~400 times" strain-energy ratio (p. 4) feed no model in this record.
