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
