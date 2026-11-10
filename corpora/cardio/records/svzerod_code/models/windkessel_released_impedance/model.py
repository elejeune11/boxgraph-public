"""Adapter: runs the released svZeroDSolver's Windkessel block (RCR, WindkesselBC) under a sinusoidal
inflow and returns its input impedance at that frequency.

Network: FLOW inlet q(t) = Q0 + Q1 sin(2 pi f t) -> BloodVessel R = 0 -> RCR outlet (proximal
resistance Rp_code = Rc, capacitance C, distal resistance Rd = Rp, distal pressure 0). The solver
starts from its steady solution and runs n_tau time constants Rp C (a setting) plus two periods; over
the last period the first Fourier coefficients of inlet pressure and flow give
  modulus = |P1| / |Q1|,  phase = arg(P1 / Q1) in degrees.
Ports are in westerhof1971's units (g/cm^4/s, cm^4 s^2/Mg, Hz); the configuration is in cgs
(1 g/cm^4/s = 1 dyn s/cm^5; 1 cm^4 s^2/Mg = 1e-6 cm^5/dyn). The probe flow (Q0, Q1) is a setting:
the block is linear, so the impedance does not depend on it.
The solver runs in its own interpreter: simulate.py, beside this file.
"""
import cmath
import json
import math
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
    n = int(settings.get("n_pts", 401))
    Q0, Q1 = float(settings.get("Q0", 100.0)), float(settings.get("Q1", 50.0))
    f = inputs["f"]
    T = 1.0 / f
    Rc, Rp, C = inputs["Rc"], inputs["Rp"], inputs["C"] * 1e-6
    cycles = int(math.ceil(float(settings.get("n_tau", 12)) * Rp * C / T)) + 2
    ts = [T * k / (n - 1) for k in range(n)]
    q = [Q0 + Q1 * math.sin(2 * math.pi * t / T) for t in ts]
    config = {
        "simulation_parameters": {
            "number_of_cardiac_cycles": cycles,
            "number_of_time_pts_per_cardiac_cycle": n,
            "output_all_cycles": False,
        },
        "boundary_conditions": [
            {"bc_name": "INFLOW", "bc_type": "FLOW", "bc_values": {"Q": q, "t": ts}},
            {"bc_name": "OUT", "bc_type": "RCR", "bc_values": {"Rp": Rc, "C": C, "Rd": Rp, "Pd": 0.0}},
        ],
        "vessels": [{"boundary_conditions": {"inlet": "INFLOW", "outlet": "OUT"}, "vessel_id": 0,
                     "vessel_length": 1.0, "vessel_name": "v0", "zero_d_element_type": "BloodVessel",
                     "zero_d_element_values": {"R_poiseuille": 0.0}}],
    }
    res = simulate(config, [["v0", "pressure_in"], ["v0", "flow_in"]])
    p, qo, t = res["v0:pressure_in"][-n:-1], res["v0:flow_in"][-n:-1], res["time"][-n:-1]
    w = 2 * math.pi / T
    P1 = sum(pk * cmath.exp(-1j * w * tk) for pk, tk in zip(p, t))
    F1 = sum(qk * cmath.exp(-1j * w * tk) for qk, tk in zip(qo, t))
    Z = P1 / F1
    return {"modulus": abs(Z), "phase": math.degrees(cmath.phase(Z))}
