"""Myosin densities of the two saddle-node points of the linear clutch model at a given E
(the boundaries of the bistability region, Fig. 5c).

At fixed E the steady states solve sigma_m = s(v; E) = P_c(v; E) / (Fst (1 - v/v0)) (Eq. 8 with
Eqs. 1, 4, 9, 11; P_c from model steady_linear). Where s is not monotonic in v, a horizontal line
sigma_m = const cuts it three times between its local maximum and local minimum: these two
extreme values of s are the myosin densities at which two steady states merge (saddle-node
points). Outputs the larger (sm_upper) and the smaller (sm_lower); NaN where s is monotonic
(below the cusp's E). The extremes are found on a log-spaced v grid and refined by a parabola
through the three grid points around each.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "liu2025_steady_linear_sn", Path(__file__).resolve().parent.parent / "steady_linear" / "model.py")
SL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SL)


def _refine(lv, s, i):
    if i <= 0 or i >= len(s) - 1:
        return float(s[i])
    y0, y1, y2 = s[i - 1], s[i], s[i + 1]
    den = y0 - 2 * y1 + y2
    if den == 0:
        return float(y1)
    d = 0.5 * (y0 - y2) / den
    return float(y1 - 0.25 * (y0 - y2) * d)


def run(inputs, settings):
    p = dict(inputs)
    p["sm"] = 1.0  # not used: the boundary is found over sigma_m
    if p.get("ly") is None:
        p["ly"] = float("inf")
    nv, nl = int(settings.get("n_v", 3000)), int(settings.get("n_l", 8000))
    vs = p["v0"] * np.logspace(-4, -1e-4, nv)
    g = SL.Grid(p, p["v0"], n=nl)
    Pc, _ = SL.traction_clutch(vs, g, p)
    s = Pc / (p["Fst"] * (1 - vs / p["v0"]))
    lv = np.log(vs)
    ds = np.diff(s)
    ext = [i + 1 for i in range(len(ds) - 1) if np.sign(ds[i]) != np.sign(ds[i + 1]) and ds[i] != 0]
    if len(ext) < 2:
        nan = float("nan")
        return {"sm_upper": nan, "sm_lower": nan}
    vals = sorted(_refine(lv, s, i) for i in ext[:2])
    return {"sm_upper": vals[1], "sm_lower": vals[0]}
