# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): olufsen1999's
# structured-tree parameters measured on 'Human Left Coronary graph.mat'. The bifurcations are those of
# tree_branching (its _nodes, one mother and two daughters by the flow of network_solution's _solve);
# the elements and their flows are network_solution's.
#   gamma = (dS/dL)^2, eta = (dL^2 + dS^2)/dM^2 (olufsen1999 Eq. 20); dL/dM = sqrt(A/(1 + S^2)) from
#   tree_branching's S = dS/dL and A = eta
#   xi: root of (dL/dM)^x + (dS/dM)^x = 1 (Eq. 19), by bisection in ln x on [e^-5, e^12]; no root
#   (+inf) where dL >= dM
#   lrr = l/(d/2); R_root = (P_up - P_cap)/Q, P_up = P_mid + Q/(2 g) with g the element's Poiseuille
#   conductance; p = -slope of ln R_root on ln(d/2)
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TB = _load("schwarz_tree_branching", os.path.join("..", "tree_branching", "model.py"))
NS = TB.NS


def _xi(uL, uS):
    lo, hi = np.full(len(uL), -5.0), np.full(len(uL), 12.0)
    with np.errstate(over="ignore", under="ignore"):
        for _ in range(80):
            mid = (lo + hi) / 2
            x = np.exp(mid)
            pos = uL ** x + uS ** x > 1
            lo, hi = np.where(pos, mid, lo), np.where(pos, hi, mid)
    return np.where(uL < 1, np.exp((lo + hi) / 2), np.inf)


def run(inputs, settings):
    sol_in = {k: inputs[k] for k in ("P_in", "P_cap", "Hd", "mu_p")}
    t = TB.T.load(settings["file"])
    r = TB._nodes(t, sol_in, {})
    lo_m = inputs["d_lo"] * 1e-6
    keep = r["dM"] >= lo_m
    dM, S, A = r["dM"][keep], r["S"][keep], r["A"][keep]
    uL = np.sqrt(A / (1 + S ** 2))
    xi = _xi(uL, S * uL)
    out = {"n_nodes": float(len(dM)), "gamma_median": float(np.median(S ** 2)),
           "eta_median": float(np.median(A)), "xi_median": float(np.median(xi)),
           "share_no_xi": float(100.0 * np.mean(~np.isfinite(xi)))}

    net = NS._network(settings["file"])
    sol = NS._solve(net, inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"])
    d = sol["d"]
    ln = np.r_[net["ie_l"], net["se_l"]]
    g = np.r_[sol["g_ie"], sol["g_seg"]]
    Q = sol["Q"]
    e = d >= lo_m
    lrr = ln[e] / (d[e] / 2)
    q1, med, q3 = np.percentile(lrr, [25, 50, 75])
    out.update({"n_elements": float(e.sum()), "lrr_median": float(med), "lrr_q1": float(q1), "lrr_q3": float(q3)})
    f = e & (Q > 0)
    R = (sol["P"][f] + Q[f] / (2 * g[f]) - inputs["P_cap"]) / Q[f]
    slope = np.polyfit(np.log(d[f] / 2), np.log(R), 1)[0]
    out["p_dc"] = float(-slope)
    return out
