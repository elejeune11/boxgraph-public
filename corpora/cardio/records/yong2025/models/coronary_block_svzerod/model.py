# The paper's coronary territories (Ra - Ca - Rmicro(t) - Cm with P_im - Rv) run in the released
# svZeroDSolver as open-loop boundary conditions: CORONARY_VAR_RES (src/model/
# OpenLoopCoronaryVarResBC.cpp, get_Ram, lines 9-38) for the time-varying resistance, CORONARY
# (OpenLoopCoronaryBC.cpp) for the constant one. The block is open loop, so its inlet pressure,
# intramyocardial pressure and (constant) venous pressure come from the closed-loop rebuild
# coronary_closed_loop on the same inputs: inlet = aortic-root pressure, P_im = imp_ratio x
# ventricular pressure (Eq. 12), P_v = cycle-mean right atrial pressure (the block takes one
# number). The solver's inlet flow is turned into the distal (intramural) flow through Rmicro,
# Q - Ca d(P - Ra Q)/dt, as the paper reports. Statistics as in Eqs. 13-14, over the cycle the
# closed-loop rebuild starts at mitral valve closure. No I/O except the solver subprocess.
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PYTHON = ROOT / "corpus" / "cardio" / "envs" / "sim" / "bin" / "python"
TERR = ("lad", "lcx", "rca")


def _base():
    spec = importlib.util.spec_from_file_location(
        "yong2025_coronary_closed_loop", HERE.parent / "coronary_closed_loop" / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _config(p, settings, drive, Pv, variable, imp):
    T = p["T"]
    n = len(drive["t"])
    bcs, vessels = [], []
    for i, k in enumerate(TERR):
        pim = drive["pim_" + k] if imp else [0.0] * n
        vals = {"Ra1": p["Ra_" + k], "Rv1": p["Rv_" + k], "Ca": p["Ca_" + k], "Cc": p["Cm_" + k],
                "Pim": pim, "P_v": Pv, "t": drive["t"]}
        if variable:
            frac = (p["frac_rca"] if k == "rca" else p["frac_lca"]) / 100.0
            kk = p["k_rca"] if k == "rca" else p["k_lca"]
            kph = p["k_ph"] if k == "rca" else 1.0
            Tvc = p["Tvc_rv"] if k == "rca" else p["Tvc_lv"]
            Tvr = p["Tvr_rv"] if k == "rca" else p["Tvr_lv"]
            # Eq. 11 as printed: sqrt(R_max) = kPH sqrt(k Rbar), so R_max = kPH^2 k Rbar
            vals.update({"Ra2_min": frac * p["Rm_" + k], "Ra2_max": kph * kph * kk * p["Rm_" + k],
                         "T_vc": Tvc, "T_vr": Tvr})
            bct = "CORONARY_VAR_RES"
        else:
            vals["Ra2"] = p["Rm_" + k]
            bct = "CORONARY"
        bcs.append({"bc_name": "IN_" + k, "bc_type": "PRESSURE",
                    "bc_values": {"P": drive["p_in"], "t": drive["t"]}})
        bcs.append({"bc_name": "COR_" + k, "bc_type": bct, "bc_values": vals})
        vessels.append({"vessel_id": i, "vessel_name": "branch%d_seg0" % i, "vessel_length": 1.0,
                        "zero_d_element_type": "BloodVessel",
                        "zero_d_element_values": {"R_poiseuille": 0.0},
                        "boundary_conditions": {"inlet": "IN_" + k, "outlet": "COR_" + k}})
    sim = {"number_of_cardiac_cycles": int(settings["n_cycles"]),
           "number_of_time_pts_per_cardiac_cycle": int(round(T / float(settings["dt"]))) + 1,
           "output_all_cycles": False}
    return {"boundary_conditions": bcs, "vessels": vessels, "simulation_parameters": sim}


def output_names():
    return [f"{s}_{k}" for k in TERR for s in ("Qs_mean", "Qd_mean", "Qs_peak", "Qd_peak", "Q_mean", "pDSFR", "mDSFR")]


def run(inputs, settings):
    nan = float("nan")
    base = _base()
    p = dict(inputs)
    dt = float(settings["dt"])
    T = p["T"]
    n = int(round(T / dt))
    rec = base.simulate(p, settings)
    res = base._cycle(rec, T, dt) if rec else None
    if res is None or res[1] is None:
        return {k: nan for k in output_names()}
    cyc, i_es = res
    last = rec[-n:]                       # phases dt, 2dt, ..., T of the last cycle
    imp = bool(settings.get("imp", True))
    ratio = p["imp_ratio"]
    IX = base.IX

    def series(f):
        v = [f(r) for r in last]
        return [v[-1]] + v                # phase 0 equals phase T (periodic)
    drive = {"t": [round(i * dt, 10) for i in range(n + 1)],
             "p_in": series(lambda r: float(r["x"][IX["ao"]])),
             "pim_lad": series(lambda r: ratio * float(r["x"][IX["lv"]])),
             "pim_lcx": series(lambda r: ratio * float(r["x"][IX["lv"]])),
             "pim_rca": series(lambda r: ratio * float(r["x"][IX["rv"]]))}
    Pv = float(np.mean([r["x"][IX["ra"]] for r in last]))
    cfg = _config(p, settings, drive, Pv, bool(settings.get("variable_resistance", True)), imp)
    env = dict(os.environ, SVV_TELEMETRY_DISABLED="1")
    proc = subprocess.run([str(PYTHON), "-I", str(HERE / "run_svzerod.py")], input=json.dumps(cfg),
                          capture_output=True, text=True, env=env, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError("svZeroDSolver failed: " + proc.stderr[-2000:])
    data = json.loads(proc.stdout)
    phase0 = int(round((cyc[0]["t"] % T) / dt)) % n
    out = {}
    for i, k in enumerate(TERR):
        d = data["branch%d_seg0" % i]
        t = np.array(d["time"])
        q = np.array(d["flow_in"])
        pin = np.array(d["pressure_in"])
        ph = np.rint((t % T) / dt).astype(int) % n
        Q = np.zeros(n)
        P = np.zeros(n)
        Q[ph] = q
        P[ph] = pin
        pca = P - p["Ra_" + k] * Q
        dpca = (np.roll(pca, -1) - np.roll(pca, 1)) / (2.0 * dt)
        qd = Q - p["Ca_" + k] * dpca     # flow through Rmicro (distal, intramural)
        qd = list(np.roll(qd, -phase0))  # start at mitral valve closure
        st = base._stats([float(v) for v in qd], i_es, dt, settings.get("dsfr", "integral"))
        for s, v in st.items():
            out[f"{s}_{k}"] = v
    return out
