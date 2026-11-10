"""Adapter: runs the released svZeroDSolver's open-loop coronary block (CORONARY, OpenLoopCoronaryBC) on
the two LAD outlets downstream of kim2010's stenosis (c and d), fed at a constant pressure.

Network: PRESSURE inlet (constant P) -> BloodVessel R = 0 -> NORMAL_JUNCTION -> two BloodVessels R = 0
-> CORONARY outlets c and d, each at a constant intramyocardial pressure Pim and venous pressure Pv.
Output: the flow through the inlet vessel (c plus d) at the end of the run. The solver starts from its
own steady solution (steady_initial, its default) and the inputs are constant, so this is the steady
(mean) flow. Ports are in kim2010's units (Table 3: R in 10^3 dyn s/cm^5, C in 10^-6 cm^5/dyn); the
configuration is in cgs. The solver runs in its own interpreter: simulate.py, beside this file.
"""
import json
import os
import subprocess

MMHG = 1333.22387415  # dyn/cm^2 per mmHg


def _sim_python():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.environ.get("BOXGRAPH_SOURCE")
    if src:
        cand = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(src))), "envs", "sim", "bin", "python")
        if os.path.exists(cand):
            return cand
    root = os.path.abspath(os.path.join(here, *[".."] * 6))
    return os.path.join(root, "corpus", "cardio", "envs", "sim", "bin", "python")


def simulate(config, columns):
    here = os.path.dirname(os.path.abspath(__file__))
    req = json.dumps({"config": config, "columns": columns})
    out = subprocess.run([_sim_python(), "-I", os.path.join(here, "simulate.py")], input=req,
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError(f"svZeroDSolver failed: {out.stderr[-2000:]}")
    return json.loads(out.stdout)


def _coronary(name, inputs, sfx):
    return {"bc_name": name, "bc_type": "CORONARY", "bc_values": {
        "Ra1": inputs["Ra_" + sfx] * 1e3, "Ra2": inputs["Ram_" + sfx] * 1e3, "Rv1": inputs["Rv_" + sfx] * 1e3,
        "Ca": inputs["Ca_" + sfx] * 1e-6, "Cc": inputs["Cim_" + sfx] * 1e-6,
        "Pim": [inputs["Pim"] * MMHG] * 2, "t": [0.0, 1.0], "P_v": inputs["Pv"] * MMHG}}


def _vessel(i, name, bcs):
    return {"boundary_conditions": bcs, "vessel_id": i, "vessel_length": 1.0, "vessel_name": name,
            "zero_d_element_type": "BloodVessel", "zero_d_element_values": {"R_poiseuille": 0.0}}


def run(inputs, settings):
    config = {
        "simulation_parameters": {
            "number_of_cardiac_cycles": int(settings.get("n_cycles", 2)),
            "number_of_time_pts_per_cardiac_cycle": int(settings.get("n_pts", 11)),
        },
        "boundary_conditions": [
            {"bc_name": "INLET", "bc_type": "PRESSURE", "bc_values": {"P": [inputs["P"] * MMHG] * 2, "t": [0.0, 1.0]}},
            _coronary("OUT_c", inputs, "c"),
            _coronary("OUT_d", inputs, "d"),
        ],
        "junctions": [{"inlet_vessels": [0], "junction_name": "J0", "junction_type": "NORMAL_JUNCTION",
                       "outlet_vessels": [1, 2]}],
        "vessels": [_vessel(0, "lad", {"inlet": "INLET"}), _vessel(1, "c", {"outlet": "OUT_c"}),
                    _vessel(2, "d", {"outlet": "OUT_d"})],
    }
    res = simulate(config, [["lad", "flow_in"]])
    return {"Q": res["lad:flow_in"][-1]}
