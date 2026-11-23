# Substrate stiffness of maximal time-averaged traction in the mean-field model (Eqs. 3-4), in
# dimensional parameters. T* is computed by mean_field's solver (loaded from that model's file)
# at n_points log-spaced values of K in [K_min, K_max]; the optimum is the vertex of a parabola
# in log10 K through the largest value and its two neighbours. ks_opt = K_opt nc kc (pN/nm),
# T_max = nc Fb T*max.
import importlib.util
import math
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "alonsomatilla2023_mean_field", Path(__file__).resolve().parent.parent / "mean_field" / "model.py")
_mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mf)


def run(inputs, settings):
    i = inputs
    F = i["nm"] * i["Fm"] / (i["nc"] * i["Fb"])
    tau = i["kon"] / i["koff"]
    om = i["vu"] * i["kc"] / (i["Fb"] * i["koff"])
    Ks = np.geomspace(float(settings["K_min"]), float(settings["K_max"]), int(settings["n_points"]))
    Ts = np.array([_mf._solve(F, tau, om, float(K), settings)[0] for K in Ks])
    k = int(np.argmax(Ts))
    u = np.log10(Ks)
    if 0 < k < len(Ks) - 1:
        a, b, c = np.polyfit(u[k - 1:k + 2], Ts[k - 1:k + 2], 2)
        uo = -b / (2 * a) if a < 0 else u[k]
        To = c - b * b / (4 * a) if a < 0 else Ts[k]
    else:
        uo, To = u[k], Ts[k]          # at the end of the scan: the scan range is too narrow
    return {"ks_opt": 10 ** uo * i["nc"] * i["kc"], "T_max": float(To) * i["nc"] * i["Fb"]}
