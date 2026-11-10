# Reading log of schwarz_data

## 2026-11-06: first reading

The release without its network file (see source.yaml, notes). Workbook adapters, the release's
stated values, and the paper's printed values copied in for comparison.

## 2026-11-07: second pass, the network file

`Human Left Coronary graph.mat` (SHA-1 7be3d8143761272d9d963952daf7b17bf5985185, downloaded from the
repository) is now in the release folder. It was read with
`scipy.io.loadmat(path, squeeze_me=True, struct_as_record=False)`; nothing of it is copied into the
record.

Kept: everything of the first reading. Added:

- `version`: the new digest of the folder, which covers the network file.
- Model `network_solution` (our solver; `software: true` only to read the file at run time): Eq. 3
  and Eq. 5 per segment, sinks in series with `TreeQ.SE.Gdist`, Kirchhoff at the internal nodes,
  sparse solve; class medians, power-law fits, the paper's flow, shear stress and perfusion statistics.
- Runs `run_net_release` (the pressures stored in `TreeQ.SE.sourceP`, Hd 0.45, plasma viscosity
  1.0 mPa s), `run_net_paper` (the paper's 90/20 mmHg and Hd 0.4), `run_net_release_classes` (class
  medians at the workbook's classes 1-11), and three derived runs.
- Data: the stored boundary pressures, eight stored solution values (field paths), the workbook's
  class medians of classes 1-11 (cells named), and six more values printed in the paper.
- Added inputs: `Hd_release_added`, `mu_p_release_added`, `mu_p_paper_added`.
- Quantities: `discharge_hematocrit`, `plasma_viscosity`, `segment_conductance`,
  `distal_conductance`, `centerline_velocity` (schwarz2020's ids).
- Questions: `q_hematocrit`, `q_class_rule`, `q_typed_precision`, `q_gdist_law`; second-pass
  paragraphs added to `q_pressure_conversion`, `q_velocity_flow_fits`, `q_viscosity_label`,
  `q_G_exponent_sign`, `q_wss_peak`, `q_flow_ratio_source`, `q_pressure_fraction_source`,
  `q_network_absent`, `q_no_validation_vs_schwarz2020`.

Changed because the network shows it wrong:

- `q_pressure_conversion` said the network solution used 11970 and 2660 N/m2. That came from the
  guide (line 120). The network's `TreeQ.SE.sourceP` holds 11998.8 and 2666.4 N/m2 (x 133.32), and
  the stored solution follows from these. The question keeps its first text about the guide and now
  says what the file holds. The pressure fraction run of the first pass (`run_P_fraction_100um`)
  still divides by the guide's 11970 N/m2, as it did; the second pass adds
  `run_net_P_fraction_100um` with the stored inlet pressure.
- `q_viscosity_label` said the plasma viscosity of the final version was unstated. That is still
  true of the text, but the stored conductances fix it (1.0 mPa s with Hd 0.45); the answer is added.
- `q_network_absent` said the network could not be rerun. That paragraph stays; what is still
  absent and unchecked is added.
- source.yaml `notes`: rewritten to cover the network.

## 2026-11-08: third pass, the rest of the release

Now in the folder, each downloaded from the repository and checked against its SHA-1:
`Human Left Coronary skeleton.txt`, `Topology data.xlsx`, `final_tree_bifurcation_summary_all-ld.xlsx`,
`termseg_density.xlsx` and `Gdistal variations.xlsx`. Only the release's copy of the paper's PDF is left
out. The skeleton was streamed with numpy in blocks of lines and the workbooks with our own streaming
xlsx reader; nothing of them is copied into the record.

Kept: everything of the first two readings. Added:

- `version`: the new digest of the folder.
- Models (all ours; `software: true` only to read the files at run time):
  `tree_table1` (Table 1 per diameter class from the network, and the segment lengths of Fig. 2B;
  shared network reader `_tree.py`), `tree_summary` (Table 1's totals and bottom rows, node types,
  loops, territory-volume quartiles), `tree_branching` (Eqs. 1-2 at the flow-directed bifurcations:
  Fig. 3-4 class statistics and group sizes, the p. 9 symmetry, the p. 5 area growth and its linear
  fit; flow from `network_solution`'s solver), `bifurcation_workbook`, `termseg_workbook`,
  `topology_workbook` (the same results recomputed from each workbook's data points),
  `stochastic_table2` (Table 2 from the per-element sheets of 'Gdistal variations.xlsx'; streaming
  reader `_xlsx_stream.py`) and `skeleton_network` (the skeleton against the network).
- Runs `run_t1_classes`, `run_t1_summary`, `run_branch_classes`, `run_branch`, `run_branch_rules`,
  `run_bifwb_classes`, `run_bifwb`, `run_termwb_classes`, `run_termwb`, `run_topowb_classes`,
  `run_topowb`, `run_table2`, `run_skeleton`, and their comparisons (`cmp_t1_*`, `cmp_wb*`,
  `cmp_t2*`, `cmp_gdist_*`, `cmp_skel_*`, `cmp_f4_*`, `cmp_A_*`, `cmp_S_*`, ...).
- Data: Table 1 (all columns and rows) and Table 2 of the paper, the p. 5 topology and area-growth
  values, the p. 8 territory-volume quartiles, the p. 9 symmetry, the group sizes printed in Fig. 4;
  the guide's skeleton counts and neighbour slots; the workbook's own Table 2 (cells named); two more
  stored mid-element pressures.
- Quantities for the new statistics (shares, densities, percentiles, node shares, loops, symmetry and
  area-growth statistics, Table 2's CV, MAD, PCC and beta, skeleton counts).
- Questions: `q_class_edges`, `q_outlier_rules`, `q_area_growth_fit`, `q_table2_reading`,
  `q_stored_solution_median_g`, `q_skeleton_slots`, `q_skeleton_diameters`, `q_region_volume`,
  `q_figure_curves`; third-pass paragraphs in `q_network_absent`, `q_hidden_choices`, `q_gdist_law`,
  `q_terminal_includes_inlets`, `q_typed_precision`, `q_no_validation_vs_schwarz2020_network`.

Changed because the new files show it wrong: nothing that the record asserted. `q_network_absent` no
longer applies to these files; it keeps its earlier text, and a third paragraph says what the runs on
them show. `q_hidden_choices` said the branching analysis excluded nodes by the 1.15 rule and short
elements, as the guide says; the workbook sheets and the paper's printed numbers show that the
results the paper prints were taken on all nodes (`q_outlier_rules`); the question keeps its text and
gains that paragraph. `q_gdist_law` said the imputed conductances are 'the in silico medians the paper
describes'; the Table 2 workbook now shows it by a run (`q_stored_solution_median_g`).

A note on the build: `skeleton_network` takes CVlim as a setting (1, the datum `CVlim`), not as an
input. As an input, its printed '1' was given a rounding range of 0.5-1.5, which was wide enough to turn
the skeleton-diameter comparison into a spurious 'reproduced'.
