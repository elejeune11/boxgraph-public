"""Adapter: grows one open-loop tree with the released svVascularize (svv, imported from the code folder
BOXGRAPH_SOURCE in the separate svv environment; grow.py) at svv's own default parameters, and reports
how far the grown tree satisfies the paper's tree equations, what svv's own check functions recompute
from it, and what svv's own 0D export of it gives when run with svZeroDSolver.

Nothing is fitted. Everything below is arithmetic on the numbers svv returns (our code):

  bifurcations = vessels with two children; d = 2 r (svv's stored radius, column 21, what svv exports)
  Eq. S6 identity:   beta_L^gamma + beta_R^gamma with svv's stored ratios (columns 23-24)
  Eq. S5:            (r_L^gamma + r_R^gamma) / r_parent^gamma with svv's stored radii, and again with
                     the radii svv's own check functions give (grow.py: naive, then Eq. S8, then
                     naive_radius)
  radius deviation:  |r_stored / r_check - 1| per vessel; R* deviation at the root likewise
  Eq. S3:            |Q_parent - Q_L - Q_R| / Q_parent per bifurcation; terminal flows against svv's
                     terminal flow
  schwarz2020:       A = (dL^2 + dS^2) / dM^2, S = dS / dL; medians over all bifurcations and over
                     mothers wider than d_A_large_um (A) and d_S_large_um (S)
  0D export:         svv's export_0d_simulation (steady, its defaults) run by svZeroDSolver:
                     P_root_0d = (P_in + P_term_svv) in mmHg (svv's own factor), the root pressure the exported
                     model needs when its outlets are held at svv's terminal pressure (the steady model is
                     resistive, so a uniform outlet pressure only shifts every pressure; the export itself
                     sets Pd = 0); P_root_0d_mu the same with every exported vessel resistance multiplied
                     by svv's density (the viscosity svv's growth uses, nu * rho, in place of the
                     export's nu); mu_export = R_poiseuille pi r^4 / (8 l) of the exported vessels (median);
                     outlet resistances, outlet flows against svv's terminal flow, outlet pressures.
"""
import json
import os
import subprocess

import numpy as np

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


def grow(req):
    req = dict(req, source=_source())
    env = dict(os.environ)
    env["SVV_TELEMETRY_DISABLED"] = "1"
    proc = subprocess.run([_find("corpus", "cardio", "envs", "sim", "bin", "python"), "-I",
                           os.path.join(_HERE, "grow.py")], input=json.dumps(req, sort_keys=True),
                          capture_output=True, text=True, env=env, cwd=_HERE, timeout=3600)
    if proc.returncode != 0:
        raise RuntimeError(f"svv growth failed: {proc.stderr[-3000:]}")
    return json.loads(proc.stdout)


def _arr(res, k):
    return np.array([np.nan if x is None else x for x in res[k]], dtype=float)


def statistics(res, settings):
    left, right = _arr(res, "left"), _arr(res, "right")
    radius, flow = _arr(res, "radius"), _arr(res, "flow")
    lbif, rbif = _arr(res, "lbif"), _arr(res, "rbif")
    rchk, rstar, rstar_chk = _arr(res, "check_radius"), _arr(res, "rstar"), _arr(res, "check_rstar")
    p = res["params"]
    gamma = p["murray_exponent"]
    bif = np.where(~np.isnan(left) & ~np.isnan(right))[0]
    term = np.where(np.isnan(left) & np.isnan(right))[0]
    li, ri = left[bif].astype(int), right[bif].astype(int)
    d_um = 2e4 * radius
    dM, d1, d2 = d_um[bif], d_um[li], d_um[ri]
    dL, dS = np.maximum(d1, d2), np.minimum(d1, d2)
    A, S = (dL ** 2 + dS ** 2) / dM ** 2, dS / dL
    bigA, bigS = dM > float(settings["d_A_large_um"]), dM > float(settings["d_S_large_um"])
    msum = lbif[bif] ** gamma + rbif[bif] ** gamma
    rsum = (radius[li] ** gamma + radius[ri] ** gamma) / radius[bif] ** gamma
    csum = (rchk[li] ** gamma + rchk[ri] ** gamma) / rchk[bif] ** gamma
    dev = np.abs(radius / rchk - 1.0)
    nan = float("nan")
    # the same statistics on the radii svv's own check gives (Eq. S8 and the ratios, exactly Eq. S5)
    c_um = 2e4 * rchk
    cM, c1, c2 = c_um[bif], c_um[li], c_um[ri]
    cL, cS = np.maximum(c1, c2), np.minimum(c1, c2)
    Ac, Sc = (cL ** 2 + cS ** 2) / cM ** 2, cS / cL
    cbigA, cbigS = cM > float(settings["d_A_large_um"]), cM > float(settings["d_S_large_um"])
    out = {
        "n_terminals_grown": float(res["n_terminals"]), "n_segments": float(len(radius)),
        "root_diameter": float(d_um[0]), "min_diameter": float(np.min(d_um)),
        "domain_volume": float(res["domain_volume"]), "t_grow": float(res["t_grow"]),
        "beta_sum_max": float(np.max(msum)), "beta_sum_min": float(np.min(msum)),
        "radius_sum_max": float(np.max(rsum)), "radius_sum_min": float(np.min(rsum)),
        "radius_sum_median": float(np.median(rsum)),
        "check_radius_sum_max": float(np.max(csum)), "check_radius_sum_min": float(np.min(csum)),
        "radius_dev_max": float(np.max(dev)), "frac_radius_dev_1pct": float(np.mean(dev > 0.01)),
        "root_radius_dev": float(abs(radius[0] / rchk[0] - 1.0)),
        "rstar_root_dev": float(abs(rstar[0] / rstar_chk[0] - 1.0)),
        "flow_sum_dev_max": float(np.max(np.abs(flow[bif] - flow[li] - flow[ri]) / flow[bif])),
        "terminal_flow_dev_max": float(np.max(np.abs(flow[term] / p["terminal_flow"] - 1.0))),
        "A_median_all": float(np.median(A)), "S_median_all": float(np.median(S)),
        "A_median_large": float(np.median(A[bigA])) if bigA.any() else nan,
        "S_median_large": float(np.median(S[bigS])) if bigS.any() else nan,
        "n_bif_A_large": float(bigA.sum()), "n_bif_S_large": float(bigS.sum()),
        "A_median_large_check": float(np.median(Ac[cbigA])) if cbigA.any() else nan,
        "S_median_large_check": float(np.median(Sc[cbigS])) if cbigS.any() else nan,
    }
    z = res["zerod"]
    length = _arr(res, "length")
    Rp = np.array(z["R_poiseuille"], dtype=float)
    scale = 1.0 / p["mmhg"]                                          # svv's pressure unit -> mmHg
    outl = z["outlets"]
    q_out = np.array([o["Q_out"] for o in outl], dtype=float)
    out.update({
        "P_root_0d": (z["P_in"] + p["terminal_pressure"]) * scale,
        "P_root_0d_mu": (z["P_in"] * p["fluid_density"] + p["terminal_pressure"]) * scale,
        "mu_export": float(np.median(Rp * np.pi * radius ** 4 / (8.0 * length))) * 100.0,   # poise -> cP
        "outlet_R_max": float(max(o["R"] for o in outl)),
        "n_outlets": float(len(outl)),
        "outlet_flow_dev_max": float(np.max(np.abs(q_out / p["terminal_flow"] - 1.0))),
        "P_out_max": float(max(abs(o["P_out"]) for o in outl)) * scale,
    })
    return out


def run(inputs, settings):
    req = {"seed": int(settings["seed"]), "n_terminals": int(round(inputs["n_terminals"])),
           "domain": settings.get("domain", "cube"), "params": {}, "export_0d": True,
           "seed_order": settings.get("seed_order", "before")}
    if req["domain"] == "cube":
        req["cube_edge"] = float(inputs["cube_edge"])
    return statistics(grow(req), settings)
