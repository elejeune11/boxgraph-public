# svv_code reading log

## First reading (boxgraph-reader, 2026-11-09, batch 7)

- Read the code folder (commit 5ca73e4; the Python files are identical to svv 0.0.57 as installed in
  corpus/cardio/envs/sim): svv/tree (Tree, TreeParameters, root, bifurcation, c_update), svv/domain (Domain,
  seeding), svv/simulation/fluid/rom/zero_d/zerod_tree.py (0D export), Copyright-Notice.txt, setup.py.
- Entered the default tree parameters, the growth step's hidden settings and the 0D export's defaults, each
  tied to sexton2025's datum where the paper prints the same parameter; copied the paper's values the runs are
  compared with.
- Models (all run the released code from the code folder): tree_parameters; resistance_update (svv's own
  c_update on one bifurcation); tree_growth and tree_biventricle (1000-terminal trees in a 1-cm cube and in
  the shipped biventricle, with svv's own check functions and svv's own 0D export run by svZeroDSolver);
  seed_repeat.
- Found before building: a seed set before Domain.create repeats a tree exactly; set after build it does
  not (q_seed: the cause of sexton2025's q_svv_nonrepeatable); c_update.update_resistance never ends on a
  table of more than one depth (q_update_resistance_loop); the 0D export finds no terminals and gives every
  outlet zero resistance (q_export_outlets), and uses the kinematic viscosity as the viscosity
  (q_viscosity_code); svv's exported radii depart from its own check (q_svv_radii).
- Nothing in other records was changed. sexton2025's q_svv_nonrepeatable is contradicted by run_seed_before
  here; its record was left as it is (this job writes only this record) and q_seed says so.
