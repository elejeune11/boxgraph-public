"""Adapter: runs the released svZeroDSolver's open-loop coronary block (CORONARY, OpenLoopCoronaryBC)
on one outlet driven by a sinusoidal inlet pressure and a sinusoidal intramyocardial pressure.

Network: PRESSURE inlet -> BloodVessel with R_poiseuille = 0 -> CORONARY outlet. Ports are in
kim2010's units; the configuration is written in cgs (dyn/cm^2, dyn*s/cm^5, cm^5/dyn, cm^3/s), the
units of the release's own coronary examples. The solver runs in its own interpreter (the project's
environment does not have it): simulate.py, beside this file.

  P(t)   = P_mean + P_amp sin(2 pi t / T)
  Pim(t) = Pim_mean - Pim_amp cos(2 pi t / T)

Outputs: mean, largest and smallest inflow over the last simulated cycle, at the solver's output points.
"""
import json
import math
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


def run(inputs, settings):
    T = inputs["T"]
    n = int(settings.get("n_pts", 501))
    # run long enough for the start-up to die out: n_tau times an upper bound of the bed's slowest
    # time constant, (Ca + Cim)(Ram + Rv), and at least n_cycles cycles
    tau = (inputs["Ca"] + inputs["Cim"]) * 1e-6 * (inputs["Ram"] + inputs["Rv"]) * 1e3
    cycles = max(int(settings.get("n_cycles", 10)), int(math.ceil(float(settings.get("n_tau", 12)) * tau / T)) + 2)
    ts = [T * k / (n - 1) for k in range(n)]
    w = 2 * math.pi / T
    P = [(inputs["P_mean"] + inputs["P_amp"] * math.sin(w * t)) * MMHG for t in ts]
    Pim = [(inputs["Pim_mean"] - inputs["Pim_amp"] * math.cos(w * t)) * MMHG for t in ts]
    config = {
        "simulation_parameters": {
            "number_of_cardiac_cycles": cycles,
            "number_of_time_pts_per_cardiac_cycle": n,
            "output_all_cycles": False,
        },
        "boundary_conditions": [
            {"bc_name": "INLET", "bc_type": "PRESSURE", "bc_values": {"P": P, "t": ts}},
            {"bc_name": "OUT", "bc_type": "CORONARY", "bc_values": {
                "Ra1": inputs["Ra"] * 1e3, "Ra2": inputs["Ram"] * 1e3, "Rv1": inputs["Rv"] * 1e3,
                "Ca": inputs["Ca"] * 1e-6, "Cc": inputs["Cim"] * 1e-6,
                "Pim": Pim, "t": ts, "P_v": inputs["Pv"] * MMHG}},
        ],
        "vessels": [{
            "boundary_conditions": {"inlet": "INLET", "outlet": "OUT"},
            "vessel_id": 0, "vessel_length": 1.0, "vessel_name": "v0",
            "zero_d_element_type": "BloodVessel", "zero_d_element_values": {"R_poiseuille": 0.0}}],
    }
    res = simulate(config, [["v0", "flow_in"]])
    q = res["v0:flow_in"]
    q_cycle = q[:-1] if len(q) == n else q  # the last output point repeats the first one of the cycle
    return {"Q_mean": sum(q_cycle) / len(q_cycle), "Q_max": max(q), "Q_min": min(q)}
