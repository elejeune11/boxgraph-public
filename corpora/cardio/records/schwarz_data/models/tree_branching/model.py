# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): the branching
# statistics of schwarz2020 (Eqs. 1-2, Figs. 3-4, pp. 5 and 9) recomputed from 'Human Left Coronary
# graph.mat'. Mother and daughters are assigned by flow direction (p. 4), the flow being that of our own
# Poiseuille-Kirchhoff solution of the network (network_solution, whose _solve is called here on the
# same inputs as run_net_release). At every internal node the inflowing elements are mothers and the
# outflowing ones daughters; the statistics use the nodes with one mother and two daughters, as the
# workbook 'final_tree_bifurcation_summary_all-ld.xlsx' does (its sheet 'moth diam - daught symmetry').
#   S = dS / dL (Eq. 1); A = (dL^2 + dS^2) / dM^2 (Eq. 2)
#   per mother diameter class (Table 1's classes, lower bound d): number of nodes, median and quartiles
#   of S, and the number of nodes and median A with S > 0.5 and S <= 0.5 (Fig. 4's two groups; the
#   group sizes printed in Fig. 4 put S = 0.5 exactly in the lower group)
#   p. 9: median S for dM > d_S_large; p. 5: median A for dM > d_A_large; p. 5: least-squares fit
#   A = c_d dM + c_S S + c_0 over d_fit_lo <= dM <= d_fit_hi, dM in m (c_d) and in mm (c_d_mm)
# Settings ratio_limit and require_l_gt_d apply the guide's outlier rules (line 235): drop nodes whose
# larger daughter exceeds ratio_limit times the mother, and nodes with any element shorter than its
# diameter. null / false keep every node.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _load("schwarz_tree", os.path.join("..", "tree_table1", "_tree.py"))
NS = _load("schwarz_network_solution", os.path.join("..", "network_solution", "model.py"))
_CACHE = {}


def _nodes(t, inputs, settings):
    key = (inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"],
           settings.get("ratio_limit"), settings.get("require_l_gt_d"))
    if key in _CACHE:
        return _CACHE[key]
    net = {k: t[k] for k in ("ie_nodes", "ie_d", "ie_l", "se_node", "se_d", "se_l", "se_inlet", "se_Gdist")}
    net["n_in"] = t["n_in"]
    sol = NS._solve(net, inputs["P_in"], inputs["P_cap"], inputs["Hd"], inputs["mu_p"])
    q_ie, q_se = sol["q_ie"], sol["q_se"]
    a, b = t["ie_nodes"][:, 0], t["ie_nodes"][:, 1]
    # (node, diameter, length, is_mother) for every element end
    node = np.r_[a, b, t["se_node"]]
    d = np.r_[t["ie_d"], t["ie_d"], t["se_d"]]
    ln = np.r_[t["ie_l"], t["ie_l"], t["se_l"]]
    mother = np.r_[q_ie < 0, q_ie > 0, q_se > 0]          # flow into the node
    n = t["n_in"]
    n_m = np.bincount(node, weights=mother, minlength=n)
    n_d = np.bincount(node, weights=~mother, minlength=n)
    sel = (n_m == 1) & (n_d == 2)
    order = np.lexsort((d, ~mother, node))                # per node: mother first, then daughters by d
    node_o, d_o, l_o = node[order], d[order], ln[order]
    first = np.searchsorted(node_o, np.arange(n))
    idx = np.where(sel)[0]
    i0 = first[idx]
    dM, dS, dL = d_o[i0], d_o[i0 + 1], d_o[i0 + 2]
    ok = np.ones(len(idx), bool)
    if settings.get("ratio_limit") is not None:
        ok &= dL <= settings["ratio_limit"] * dM
    if settings.get("require_l_gt_d"):
        ok &= (l_o[i0] > dM) & (l_o[i0 + 1] > dS) & (l_o[i0 + 2] > dL)
    res = {"dM": dM[ok], "S": (dS / dL)[ok], "A": ((dL ** 2 + dS ** 2) / dM ** 2)[ok],
           "n_multi_mother": float(np.sum(n_m > 1))}
    _CACHE[key] = res
    return res


def run(inputs, settings):
    t = T.load(settings["file"])
    r = _nodes(t, inputs, settings)
    dM, S, A = r["dM"], r["S"], r["A"]
    c = T.classify(dM, settings["class_edges_um"]) == T.class_index(inputs["d"], settings["class_edges_um"])
    hi, lo = c & (S > settings["S_split"]), c & (S <= settings["S_split"])   # 0.5 itself in the lower group
    _, q1, med, q3, _ = T.stats(S[c])
    out = {"n_nodes_class": float(c.sum()), "S_median": med, "S_q1": q1, "S_q3": q3,
           "n_symhi": float(hi.sum()), "n_symlo": float(lo.sum()),
           "A_median_symhi": T.stats(A[hi])[2], "A_median_symlo": T.stats(A[lo])[2]}
    out["n_nodes"] = float(len(dM))
    out["n_multi_mother"] = r["n_multi_mother"]
    out["S_median_large"] = T.stats(S[dM > inputs["d_S_large"] * 1e-6])[2]
    out["A_median_large"] = T.stats(A[dM > inputs["d_A_large"] * 1e-6])[2]
    f = (dM >= inputs["d_fit_lo"] * 1e-6) & (dM <= inputs["d_fit_hi"] * 1e-6)
    X = np.c_[dM[f], S[f], np.ones(f.sum())]
    coef, *_ = np.linalg.lstsq(X, A[f], rcond=None)
    out["c_d"], out["c_d_mm"], out["c_S"], out["c_0"] = float(coef[0]), float(coef[0]) * 1e-3, float(coef[1]), float(coef[2])
    out["fit_r2"] = float(1 - np.sum((A[f] - X @ coef) ** 2) / np.sum((A[f] - A[f].mean()) ** 2))
    out["n_fit"] = float(f.sum())
    return out
