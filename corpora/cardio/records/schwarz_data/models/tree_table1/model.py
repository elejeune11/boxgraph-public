# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): Table 1 of
# schwarz2020 per diameter class, recomputed from 'Human Left Coronary graph.mat'.
#   All       every element, TreeQ.IE and TreeQ.SE (202,184), by its diameter .d
#   Terminal  the source/sink elements TreeQ.SE (guide line 250: the two >= 400 um are the inlets)
#   LV density  terminal elements of a region (TreeQ.SE.regionID 1 LV epi, 2 LV mid, 3 LV endo; guide
#             lines 151-162) per cm^3 of that region, the region's volume taken as the sum of the
#             Voronoi volumes TreeQ.SE.VVoronoi of its terminal elements (our reading: the guide does not
#             say which volume the densities of termseg_density.xlsx 'Region' divide by)
#   Shares    percent of the column total
# Also the segment length of the class (Fig. 2B: median and quartiles over all elements of the class).
# Classes [lo, hi) with edges in metres (see _tree.edges_m); the class is named by its lower bound d.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_tree", os.path.join(_HERE, "_tree.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)


def run(inputs, settings):
    t = T.load(settings["file"])
    edges = settings["class_edges_um"]
    k = T.class_index(inputs["d"], edges)
    d_all = np.r_[t["ie_d"], t["se_d"]]
    l_all = np.r_[t["ie_l"], t["se_l"]]
    c_all, c_ie, c_se = T.classify(d_all, edges), T.classify(t["ie_d"], edges), T.classify(t["se_d"], edges)
    out = {
        "n_all": float(np.sum(c_all == k)),
        "n_internal": float(np.sum(c_ie == k)),
        "n_terminal": float(np.sum(c_se == k)),
    }
    out["share_all"] = 100.0 * out["n_all"] / len(d_all)
    out["share_terminal"] = 100.0 * out["n_terminal"] / len(t["se_d"])
    for name, rid in settings["regions"].items():
        s = t["se_region"] == rid
        vol_cm3 = float(np.nansum(t["se_V"][s])) * 1e6
        dens = float(np.sum(s & (c_se == k))) / vol_cm3
        total = float(np.sum(s)) / vol_cm3
        out["dens_" + name] = dens
        out["dshare_" + name] = 100.0 * dens / total
    _, q1, med, q3, _ = T.stats(l_all[c_all == k] * 1e6)
    out.update({"L_median": med, "L_q1": q1, "L_q3": q3})
    return out
