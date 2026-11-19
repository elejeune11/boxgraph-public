# Eq. 1 (p. 2): the 4x4 determinant condition for linear instability of a layer (0 < z < a)
# grown uniaxially, G = diag(g, 1, 1/g), on a neo-Hookean half-space. The threshold at a given
# wavelength is the smallest g > 1 at which the determinant changes sign, found by a scan in g
# followed by root bracketing. Rows 1 and 2 are both multiplied by exp(-ak) to avoid overflow;
# this scales the determinant by a positive factor and leaves its zeros unchanged.
import math

import numpy as np
from scipy.optimize import brentq


def det(g, ka, eta):
    b = 1.0 + g**4
    em = math.exp(-ka / g**2 - ka)
    ep = math.exp(ka / g**2 - ka)
    e2 = math.exp(-2.0 * ka)
    M = np.array([
        [b * em, b * ep, 2.0 * e2 * g**4, 2.0 * g**4],
        [-2.0 * g**2 * em, 2.0 * ep * g**2, -b * e2, b],
        [b * eta / 2.0 + 1.0, b * eta / 2.0 - 1.0, eta * g**4 + g**2, g**4 * eta - g**2],
        [eta + 1.0, 1.0 - eta, b * eta / (2.0 * g**2) + 1.0, 1.0 - b * eta / (2.0 * g**2)],
    ])
    return float(np.linalg.det(M))


def threshold(eta, l_over_a, g_max=4.0, n_scan=200):
    """Smallest g > 1 with det = 0 at wavelength l/a, or None below g_max."""
    ka = 2.0 * math.pi / l_over_a
    gs = np.linspace(1.0 + 1e-9, g_max, int(n_scan))
    prev = det(gs[0], ka, eta)
    for i in range(1, len(gs)):
        cur = det(gs[i], ka, eta)
        if prev == 0.0:
            return float(gs[i - 1])
        if (prev < 0) != (cur < 0):
            return brentq(det, gs[i - 1], gs[i], args=(ka, eta), xtol=1e-13, rtol=1e-13)
        prev = cur
    return None


def run(inputs, settings):
    g = threshold(inputs["eta"], inputs["l_over_a"], settings.get("g_max", 4.0), settings.get("n_scan", 200))
    return {"g": float("nan") if g is None else g}
