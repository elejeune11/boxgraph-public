# Our code (software: true only to read the released network from $BOXGRAPH_SOURCE): the mid-segment
# pressure of the released network's solution (network_solution's _solve, the same solver and inputs as
# run_net_release) over the segments of a diameter range, as a percentage of the inlet pressure. Built
# for comparisons with measured microvascular pressures given as a percentage of aortic pressure, for
# vessel classes given by a diameter range rather than by the 20 um classes of network_solution.
import importlib.util
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
    P_in, P_cap = inputs["P_in"], inputs["P_cap"]
    sol = NS._solve(net, P_in, P_cap, inputs["Hd"], inputs["mu_p"])
    d_um = sol["d"] * 1e6
    s = (d_um >= inputs["d_lo"]) & (d_um <= inputs["d_hi"])
    if not s.any():
        nan = float("nan")
        return {"n_seg": 0.0, "share_median": nan, "share_q1": nan, "share_q3": nan, "proximal_median": nan}
    share = 100.0 * sol["P"][s] / P_in
    q1, med, q3 = (float(np.percentile(share, p)) for p in (25, 50, 75))
    p_med = float(np.median(sol["P"][s]))
    return {"n_seg": float(s.sum()), "share_median": med, "share_q1": q1, "share_q3": q3,
            "proximal_median": 100.0 * (P_in - p_med) / (P_in - P_cap)}
