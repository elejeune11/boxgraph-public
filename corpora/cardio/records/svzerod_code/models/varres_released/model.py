"""Adapter: runs the released svZeroDSolver's time-varying coronary block (CORONARY_VAR_RES,
OpenLoopCoronaryVarResBC) and reads its microvascular resistance back from the pressure it needs to
pass a constant flow.

Network: FLOW inlet (constant Q, a setting) -> BloodVessel R = 0 -> CORONARY_VAR_RES with arterial and
venous resistances Ra, Rv (inputs), Ram_min, Ram_max, T_vc, T_vr (inputs), intramyocardial and venous
pressure 0, and capacitances Ca = Cim = tau_probe / (Ram_max + Rv) (tau_probe a setting, short
against Ram(t)'s variation, so the bed is purely resistive). Then P_in(t) = Q (Ra + Ram(t) + Rv), so
  Ram_mean = mean of P_in over the last cycle / Q - Ra - Rv,  Ram_peak = max P_in / Q - Ra - Rv.
Numbers are passed in the ports' units (mmHg, mL, s): the solver has no units of its own.
The solver runs in its own interpreter: simulate.py, beside this file.
"""
import json
import os
import subprocess


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
    T = inputs["T"]
    n = int(settings.get("n_pts", 1001))
    Q = float(settings.get("Q", 1.0))
    # probe capacitances from a time constant, so that they scale with the units of the inputs:
    # C (Ram_max + Rv) = tau_probe
    C = float(settings.get("tau_probe", 1e-4)) / (inputs["Ram_max"] + inputs["Rv"])
    config = {
        "simulation_parameters": {
            "number_of_cardiac_cycles": int(settings.get("n_cycles", 3)),
            "number_of_time_pts_per_cardiac_cycle": n,
            "cardiac_period": T,
            "output_all_cycles": False,
        },
        "boundary_conditions": [
            {"bc_name": "INFLOW", "bc_type": "FLOW", "bc_values": {"Q": [Q, Q], "t": [0.0, T]}},
            {"bc_name": "OUT", "bc_type": "CORONARY_VAR_RES", "bc_values": {
                "Ra1": inputs["Ra"], "Rv1": inputs["Rv"], "Ca": C, "Cc": C,
                "Pim": [0.0, 0.0], "t": [0.0, T], "P_v": 0.0,
                "Ra2_min": inputs["Ram_min"], "Ra2_max": inputs["Ram_max"],
                "T_vc": inputs["T_vc"], "T_vr": inputs["T_vr"]}},
        ],
        "vessels": [{"boundary_conditions": {"inlet": "INFLOW", "outlet": "OUT"}, "vessel_id": 0,
                     "vessel_length": 1.0, "vessel_name": "v0", "zero_d_element_type": "BloodVessel",
                     "zero_d_element_values": {"R_poiseuille": 0.0}}],
    }
    res = simulate(config, [["v0", "pressure_in"]])
    p = res["v0:pressure_in"]
    p_cycle = p[:-1] if len(p) == n else p  # the last output point repeats the first one of the cycle
    r_series = inputs["Ra"] + inputs["Rv"]
    return {"Ram_mean": sum(p_cycle) / len(p_cycle) / Q - r_series, "Ram_peak": max(p) / Q - r_series}
