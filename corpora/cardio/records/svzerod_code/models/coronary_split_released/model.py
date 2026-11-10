"""Adapter: runs the released svZeroDSolver's open-loop coronary block (CORONARY, OpenLoopCoronaryBC) on
kim2010's eleven coronary outlets (a-d LAD, e-h LCX, i-k RCA), all fed from one node with a constant
total coronary flow.

Network: FLOW inlet (constant Q_total) -> BloodVessel R = 0 -> NORMAL_JUNCTION -> eleven BloodVessels
R = 0 -> eleven CORONARY outlets with kim2010's Table 3 resistances and capacitances, each at a constant
intramyocardial pressure Pim and venous pressure Pv. Outputs: the steady flows summed over the LAD,
LCX and RCA outlets (the solver starts from its own steady solution and the inputs are constant).
This is the network kim2010's record splits the total flow on (coronary_flow_split): the same mean
pressure at every outlet. Ports are in kim2010's units; the configuration is in cgs. The solver runs in
its own interpreter: simulate.py, beside this file.
"""
import json
import os
import subprocess

MMHG = 1333.22387415  # dyn/cm^2 per mmHg
OUTLETS = {"a": "LAD", "b": "LAD", "c": "LAD", "d": "LAD", "e": "LCX", "f": "LCX", "g": "LCX", "h": "LCX",
           "i": "RCA", "j": "RCA", "k": "RCA"}


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


def run(inputs, settings):
    bcs = [{"bc_name": "INFLOW", "bc_type": "FLOW", "bc_values": {"Q": [inputs["Q_total"]] * 2, "t": [0.0, 1.0]}}]
    vessels = [{"boundary_conditions": {"inlet": "INFLOW"}, "vessel_id": 0, "vessel_length": 1.0,
                "vessel_name": "root", "zero_d_element_type": "BloodVessel",
                "zero_d_element_values": {"R_poiseuille": 0.0}}]
    for i, o in enumerate(sorted(OUTLETS), start=1):
        bcs.append({"bc_name": "OUT_" + o, "bc_type": "CORONARY", "bc_values": {
            "Ra1": inputs["Ra_" + o] * 1e3, "Ra2": inputs["Ram_" + o] * 1e3, "Rv1": inputs["Rv_" + o] * 1e3,
            "Ca": inputs["Ca_" + o] * 1e-6, "Cc": inputs["Cim_" + o] * 1e-6,
            "Pim": [inputs["Pim"] * MMHG] * 2, "t": [0.0, 1.0], "P_v": inputs["Pv"] * MMHG}})
        vessels.append({"boundary_conditions": {"outlet": "OUT_" + o}, "vessel_id": i, "vessel_length": 1.0,
                        "vessel_name": "out_" + o, "zero_d_element_type": "BloodVessel",
                        "zero_d_element_values": {"R_poiseuille": 0.0}})
    config = {
        "simulation_parameters": {
            "number_of_cardiac_cycles": int(settings.get("n_cycles", 2)),
            "number_of_time_pts_per_cardiac_cycle": int(settings.get("n_pts", 11)),
        },
        "boundary_conditions": bcs,
        "junctions": [{"inlet_vessels": [0], "junction_name": "J0", "junction_type": "NORMAL_JUNCTION",
                       "outlet_vessels": list(range(1, len(OUTLETS) + 1))}],
        "vessels": vessels,
    }
    res = simulate(config, [["out_" + o, "flow_in"] for o in sorted(OUTLETS)])
    out = {"Q_LAD": 0.0, "Q_LCX": 0.0, "Q_RCA": 0.0}
    for o, branch in OUTLETS.items():
        out["Q_" + branch] += res["out_" + o + ":flow_in"][-1]
    return out
