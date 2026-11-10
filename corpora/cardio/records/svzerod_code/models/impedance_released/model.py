"""Adapter: runs the released svZeroDSolver's impedance block (IMPEDANCE, ImpedanceBC) on a periodic
inflow and an exponential impulse response.

Network: FLOW inlet q(t) = Q0 + Q1 sin(2 pi t / T) -> BloodVessel R = 0 -> IMPEDANCE outlet, Pd = 0.
Impulse response (in the ports' units): z(t) = (Z / tau) exp(-t / tau), 0 <= t < T.
The code takes the kernel as "discrete-time convolution weights" with "no extra dt scaling"
(ImpedanceBC.cpp lines 35-36), so this adapter passes z_m = z(m dt) dt, m = 0..N-1, dt = T / N, and
sets number_of_time_pts_per_cardiac_cycle = N + 1 and steady_initial = false, as the block requires
(ImpedanceBC.h). Numbers are passed in the ports' units (dyn/cm^2, cm^3/s, s).
Outputs: mean, largest and smallest inlet pressure over the last simulated cycle (the first cycle,
before the convolution switches on, is discarded by running n_cycles >= 2).
The solver runs in its own interpreter: simulate.py, beside this file.
"""
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
    N = int(settings.get("N", 128))
    T = inputs["T"]
    dt = T / N
    ts = [k * dt for k in range(N + 1)]
    q = [inputs["Q0"] + inputs["Q1"] * math.sin(2 * math.pi * t / T) for t in ts]
    z = [inputs["Z"] / inputs["tau"] * math.exp(-m * dt / inputs["tau"]) * dt for m in range(N)]
    config = {
        "simulation_parameters": {
            "number_of_cardiac_cycles": int(settings.get("n_cycles", 4)),
            "number_of_time_pts_per_cardiac_cycle": N + 1,
            "cardiac_period": T,
            "steady_initial": False,
            "output_all_cycles": False,
        },
        "boundary_conditions": [
            {"bc_name": "INFLOW", "bc_type": "FLOW", "bc_values": {"Q": q, "t": ts}},
            {"bc_name": "OUT", "bc_type": "IMPEDANCE", "bc_values": {"z": z, "Pd": 0.0}},
        ],
        "vessels": [{"boundary_conditions": {"inlet": "INFLOW", "outlet": "OUT"}, "vessel_id": 0,
                     "vessel_length": 1.0, "vessel_name": "v0", "zero_d_element_type": "BloodVessel",
                     "zero_d_element_values": {"R_poiseuille": 0.0}}],
    }
    res = simulate(config, [["v0", "pressure_in"]])
    p = res["v0:pressure_in"]
    p_cycle = p[:-1] if len(p) == N + 1 else p
    return {"P_mean": sum(p_cycle) / len(p_cycle), "P_max": max(p), "P_min": min(p)}
