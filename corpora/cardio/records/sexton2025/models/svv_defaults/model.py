# The constants the released svVascularize (svv 0.0.57) grows a tree with when none are set: a default
# TreeParameters() read in the separate svv environment (defaults.py, `python -I`, SVV_TELEMETRY_DISABLED=1).
# svv stores a kinematic viscosity and a density and uses their product as the viscosity of Eq. S1
# (svv/tree/branch/bifurcation.py line 2162, nu = kinematic_viscosity * fluid_density); mu is that product.
import json
import os
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
MMHG = 1333.22387415          # dyn/cm^2 per mmHg


def _sim_python():
    d = _HERE
    for _ in range(10):
        cand = os.path.join(d, "corpus", "cardio", "envs", "sim", "bin", "python")
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(d)
    raise FileNotFoundError("the svv environment corpus/cardio/envs/sim was not found")


def run(inputs, settings):
    env = dict(os.environ)
    env["SVV_TELEMETRY_DISABLED"] = "1"
    proc = subprocess.run([_sim_python(), "-I", os.path.join(_HERE, "defaults.py")], capture_output=True,
                          text=True, env=env, cwd=_HERE, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(f"svv failed: {proc.stderr[-3000:]}")
    p = json.loads(proc.stdout)
    return {"gamma": p["murray_exponent"], "alpha_r": p["radius_exponent"], "alpha_l": p["length_exponent"],
            "nu": p["kinematic_viscosity"], "rho": p["fluid_density"],
            "mu": p["kinematic_viscosity"] * p["fluid_density"] * 100.0,      # poise -> cP
            "Q_term": p["terminal_flow"],
            "P_root": p["root_pressure"] / MMHG, "P_term": p["terminal_pressure"] / MMHG}
