"""Adapter: the constants the released svVascularize grows a tree with when none are set, read from a
default TreeParameters() of the code in BOXGRAPH_SOURCE (run in the separate svv environment).

mu is the viscosity svv's growth puts in Eq. S1: its kinematic viscosity times its density (root.py
line 266, bifurcation.py lines 628, 705); pressures are returned in mmHg with svv's own factor."""
import json
import os
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find(*parts):
    d = _HERE
    for _ in range(10):
        cand = os.path.join(d, *parts)
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(d)
    raise FileNotFoundError(os.path.join(*parts))


def _source():
    src = os.environ.get("BOXGRAPH_SOURCE")
    return os.path.abspath(src) if src and os.path.isdir(src) else _find("corpus", "cardio", "code", "svv_code")


def run(inputs, settings):
    env = dict(os.environ)
    env["SVV_TELEMETRY_DISABLED"] = "1"
    proc = subprocess.run([_find("corpus", "cardio", "envs", "sim", "bin", "python"), "-I",
                           os.path.join(_HERE, "params.py"), _source()],
                          capture_output=True, text=True, env=env, cwd=_HERE, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(f"svv failed: {proc.stderr[-3000:]}")
    p = json.loads(proc.stdout)
    return {"gamma": p["murray_exponent"], "alpha_r": p["radius_exponent"], "alpha_l": p["length_exponent"],
            "nu": p["kinematic_viscosity"], "rho": p["fluid_density"],
            "mu": p["kinematic_viscosity"] * p["fluid_density"] * 100.0,      # poise -> cP
            "Q_term": p["terminal_flow"],
            "P_root": p["root_pressure"] / p["mmhg"], "P_term": p["terminal_pressure"] / p["mmhg"]}
