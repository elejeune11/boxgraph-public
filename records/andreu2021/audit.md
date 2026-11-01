# Audit of andreu2021

Second, independent reading against the page images (claude-opus-5-5, 2026-11-01).

## Checked, no change

- `nf_table`, `kon_i_table`, `kc_table`, `FR_table`, `ksub_table`, `dmin_table`, `dmax_table`, `dadd_table`,
  `Fact_table` (p. 23): every value, exponent (2.11x10^-4 µm²/s) and unit (1 nN/nm, 1 µN/nm) matches the
  image of Supplementary Table 4. The origins also match the table: ref. 20 or "Adjusted".
- `dadd_text`, `Fact_methods` (p. 10), `Fact_results` (p. 5): as printed.
- `A_2p5`, `A_5`, `A_10`, `A_20` (p. 4, Fig. 2e caption): 1.5, 2, 2.5, 3 µm for 2.5, 5, 10, 20%, as printed.
- `diameter_p2`, `stretch_2p5_p2`, `freq_0p125_p2`, `speed_p2` (p. 2), and `diameter_p5`, `stretch_10_p5`,
  `stretch_20_p5`, `freq_1_p5`, `freq_2_p5`, `speed_range_p5` (p. 5): as printed.
- `clutch_stretch_sim` (p. 10): Eq. 4 (F_sub = k_sub k_c Σx_i / (k_sub + n_bound k_c)), Eq. 5
  (p = k(F)/L exp(−∫₀^F k dF / L)), Eq. 6 (F_m = ∫₀^∞ F p(F) dF) and k′ = L/F_m match the image. So do
  items 1–4 (actin breaking only while talin is folded, |v| = 2Af, Gillespie, the loading-rate
  correction) and the 1000 s output. The baseline-force lifetime (F_m − F_b)/L departs from the literal
  k′ = L/F_m, but it is already recorded as `q_lifetime_baseline`.
- `edge_speed` (pp. 2, 5, 10): |v| = 2Af with A = stretch × radius reproduces the paper's arithmetic
  (62.5 nm/s for "~60"; 2 and 8 µm/s for "2–8").
- The added inputs in `added.yaml` all have a basis. Four have no alternatives (`ln_kunf0_added`,
  `kunf_b_added`, `ksub_code_added`, `len_scale_added`; validator warnings). Choosing alternatives is a
  judgement of the first reader, so they are left as they are. `ksub_code_added` is in effect the
  alternative to `ksub_table`, and both are run.
- No transcription error was found, so no value, unit or equation was corrected.

## Added

- Supplementary Table 1, row "1 (stretch)" (p. 20). These are printed results of the paper's own edge
  estimate (notes i–ii) and were not compared. The first reader left the table out because it gives
  only orders of magnitude. The audit records it anyway, with comparisons that correctly get no verdict.
  - Quantities `cell_radius`, `cell_stiffness`, `cell_load`, `cell_loading_rate`.
  - Data `radius_supp1`, `stiffness_supp1` (p. 20), `stretch_2p5_fig1`, `stretch_20_fig1` (p. 3, Fig. 1
    caption), `freq_0p125_table4`, `freq_2_table4` (p. 23).
  - Data for each end of each range cell: `deformation_lo/hi_supp1`, `defrate_lo/hi_supp1`,
    `load_lo/hi_supp1`, `loadrate_lo/hi_supp1` (p. 20). A range of two bare powers ("10^-1 - 10^0")
    cannot be parsed as one printed value, so each end is its own datum.
  - Model `supp_table1_edge` (p. 20, notes i–ii; built from `edge_speed`), runs `run_supp1_low`
    (2.5%, 0.125 Hz) and `run_supp1_high` (20%, 2 Hz), and comparisons `cmp_supp1_*` (8).
- Not added: the per-area columns of the same row, because the adhesion area formula is unstated
  (`q_supp1_per_area`). The optical-tweezers and AFM rows were also left out, since they come from
  measured speeds and literature areas, not from a model in the record.

## New open questions

- `q_supp1_load` (unstated_model, p. 20): the load = stiffness × deformation is assumed. Note (ii) states
  it only for loading rates.
- `q_supp1_order_ranges` (reading, p. 20): taken literally, the paper's edge estimate falls outside some
  of the printed ranges: 0.0625 µm/s < 10^-1, 0.5 nN < 10^0, 16 nN/s > 10^1. Each is within an order of
  magnitude.
- `q_supp1_per_area` (unstated_input, p. 20): how the adhesion area follows from the 10 µm radius and the
  ~2 µm edge band.

## Disagreements and limits

- Minor, not recorded as questions: Eq. 6 is printed with "df" for "dF" (p. 10), and Supplementary
  Table 4 names the talin unfolding rate "K_fold" while the text says k_unf (p. 23). Both are cosmetic.
- The Fig. 2e line readings (`fig2e_line_*`, p. 4) were **not** re-checked against an overlay in this
  audit. Running `boxgraph figure check` was not permitted in this session, so a later check should open
  the overlays.
