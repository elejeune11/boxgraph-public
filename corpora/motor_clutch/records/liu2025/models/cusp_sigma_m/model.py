"""Cusp point of the linear clutch model in (E, sigma_m) (Fig. 5c,d; Results text).

The steady states at given E solve sigma_m = s(v; E) = P_c(v; E) / (Fst (1 - v/v0)), with P_c
from Eqs. 1, 4, 9, 11 (model steady_linear). Two saddle-node points (bistability) exist at E
where s(.; E) is not monotonic in v; they are born together at the cusp, the lowest E where
min_v ds/dln v reaches zero. The cusp's sigma_m is s there. Found by bisection on log E.
Outputs: sigma_m at the cusp (1/um^2), E at the cusp (Pa), and the ratio of a given myosin
density (the fitted one) to the cusp value.
"""
import importlib.util
import math
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "liu2025_steady_linear", Path(__file__).resolve().parent.parent / "steady_linear" / "model.py")
SL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SL)


def _profile(p, E, vs, nl):
    q = dict(p, E=E)
    g = SL.Grid(q, q["v0"], n=nl)
    Pc, _ = SL.traction_clutch(vs, g, q)
    s = Pc / (q["Fst"] * (1 - vs / q["v0"]))
    d = np.diff(s) / np.diff(np.log(vs))
    i = int(np.argmin(d))
    return float(d[i]), float(s[i:i + 2].mean())


def run(inputs, settings):
    p = dict(inputs)
    p["sm"] = 1.0  # not used: the cusp is found over sigma_m
    nv, nl = int(settings.get("n_v", 3000)), int(settings.get("n_l", 8000))
    vs = p["v0"] * np.logspace(-4, -1e-4, nv)
    lo, hi = math.log10(float(settings.get("E_min", 1e2))), math.log10(float(settings.get("E_max", 1e9)))
    Es = np.logspace(lo, hi, 29)
    ds = [_profile(p, E, vs, nl)[0] for E in Es]
    neg = [i for i, d in enumerate(ds) if d < 0]
    if not neg or neg[0] == 0:
        nan = float("nan")
        return {"sm_cusp": nan, "E_cusp": nan, "ratio": nan}
    a, b = math.log10(Es[neg[0] - 1]), math.log10(Es[neg[0]])
    for _ in range(30):
        m = 0.5 * (a + b)
        if _profile(p, 10 ** m, vs, nl)[0] < 0:
            b = m
        else:
            a = m
    E_c = 10 ** b
    s_c = _profile(p, E_c, vs, nl)[1]
    return {"sm_cusp": s_c, "E_cusp": E_c, "ratio": inputs["sm_fit"] / s_c}
