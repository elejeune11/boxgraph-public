# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): the lumen volume of the
# released left coronary tree's segments in a diameter window, as a fraction of the tissue volume the tree
# perfuses (the sum of TreeQ.SE.VVoronoi). Each segment, internal or source/sink, is a cylinder pi d^2 l / 4 with
# the stored d and l (network_solution's reader). Built for comparison with intramyocardial arterial blood-volume
# fractions such as spaan1981's small-artery volume fraction (0.023 of myocardial volume, p. 8).
import importlib.util
import math
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NS = _load("schwarz_network_solution", os.path.join("..", "network_solution", "model.py"))


def run(inputs, settings):
    net = NS._network(settings["file"])
    d = np.concatenate([net["ie_d"], net["se_d"]])
    l = np.concatenate([net["ie_l"], net["se_l"]])
    ok = np.isfinite(d) & np.isfinite(l)
    d_um = d * 1e6
    sel = ok & (d_um >= inputs["d_lo"]) & (d_um <= inputs["d_hi"])
    v_lumen = float(np.sum(math.pi * d[sel] ** 2 * l[sel] / 4.0))       # m^3
    v_all = float(np.sum(math.pi * d[ok] ** 2 * l[ok] / 4.0))
    v_tissue = float(np.nansum(net["se_V"]))                            # m^3
    return {
        "n_seg": float(np.sum(sel)),
        "V_lumen": v_lumen * 1e9,          # mm^3
        "V_tissue": v_tissue * 1e6,        # cm^3
        "phi": v_lumen / v_tissue,
        "share_of_tree": v_lumen / v_all,
    }
