# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): whole-network
# statistics of schwarz2020 recomputed from 'Human Left Coronary graph.mat'.
#   Table 1, bottom rows: element count; median, 10th and 90th percentile of diameter; median length,
#     for all elements (IE and SE), terminal elements (SE), and the terminal elements of the LV regions
#     (TreeQ.SE.regionID 1 epi, 2 mid, 3 endo); the region totals of terminal density (per cm^3 of the
#     summed VVoronoi of the region, as in tree_table1).
#   p. 5: the share of internal nodes connecting 3, 4 and more elements (degree counted from IE.nodes
#     and SE.node), and the number of loops: the cycle rank E - V + C of the graph (E elements, V
#     internal and source nodes, C connected components).
#   p. 8: quartiles of the perfused volume of the perfusion branches (sum of VVoronoi per PerfBranchID).
# Percentiles by numpy's linear rule.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_tree", os.path.join(_HERE, "..", "tree_table1", "_tree.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)


def run(inputs, settings):
    import scipy.sparse as sp
    import scipy.sparse.csgraph as cg

    t = T.load(settings["file"])
    out = {}
    groups = {"all": (np.r_[t["ie_d"], t["se_d"]], np.r_[t["ie_l"], t["se_l"]]), "term": (t["se_d"], t["se_l"])}
    for name, rid in settings["regions"].items():
        s = t["se_region"] == rid
        groups[name] = (t["se_d"][s], t["se_l"][s])
        vol_cm3 = float(np.nansum(t["se_V"][s])) * 1e6
        out["dens_" + name] = float(np.sum(s)) / vol_cm3
    for g, (d, l) in groups.items():
        p10, _, med, _, p90 = T.stats(d * 1e6)
        out[f"n_{g}"] = float(len(d))
        out[f"d_med_{g}"], out[f"d_p10_{g}"], out[f"d_p90_{g}"] = med, p10, p90
        out[f"l_med_{g}"] = T.stats(l * 1e6)[2]
    out["n_regions"] = out["n_epi"] + out["n_mid"] + out["n_endo"]
    n_in = t["n_in"]
    deg = np.bincount(t["ie_nodes"].ravel(), minlength=n_in) + np.bincount(t["se_node"], minlength=n_in)
    out["pct_3"] = 100.0 * np.mean(deg == 3)
    out["pct_4"] = 100.0 * np.mean(deg == 4)
    out["pct_more"] = 100.0 * np.mean(deg > 4)
    n_se = len(t["se_node"])
    E, V = len(t["ie_d"]) + n_se, n_in + t["n_sn"]
    rows = np.r_[t["ie_nodes"][:, 0], t["se_node"]]
    cols = np.r_[t["ie_nodes"][:, 1], n_in + t["se_sn"]]
    C, _ = cg.connected_components(sp.coo_matrix((np.ones(E), (rows, cols)), shape=(V, V)), directed=False)
    out["n_components"] = float(C)
    out["n_loops"] = float(E - V + C)
    out["n_in"], out["n_sn"] = float(n_in), float(t["n_sn"])
    br, vol = t["se_branch"], t["se_V"]
    ok = np.isfinite(br)
    ids, inv = np.unique(br[ok], return_inverse=True)
    vb = np.bincount(inv, weights=np.nan_to_num(vol[ok])) * 1e9       # mm^3
    _, q1, med, q3, _ = T.stats(vb)
    out.update({"V_territory_q1": q1, "V_territory_median": med, "V_territory_q3": q3})
    return out
