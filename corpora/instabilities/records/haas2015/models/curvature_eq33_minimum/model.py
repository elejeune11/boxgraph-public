# Global minimum of K^2(Lambda) of Eq. 3.3 (sin Theta is a common factor and drops out):
# coarse grid over [L_lo, L_hi], then a bounded scalar minimization around the best grid point.
import math

import numpy as np
from scipy.optimize import minimize_scalar

R2 = math.sqrt(2.0)


def _k2(L):
    D = 1.0 + np.exp(-L / R2) * ((R2 * L - 1.0) * np.sin(L / R2) - np.cos(L / R2))
    return 8.0 * R2 / D


def run(inputs, settings):
    lo, hi, n = float(settings["L_lo"]), float(settings["L_hi"]), int(settings["n_grid"])
    grid = np.linspace(lo, hi, n)
    i = int(np.argmin(_k2(grid)))
    a, b = grid[max(i - 1, 0)], grid[min(i + 1, n - 1)]
    res = minimize_scalar(_k2, bounds=(a, b), method="bounded", options={"xatol": 1e-10})
    return {"L_min": float(res.x)}
