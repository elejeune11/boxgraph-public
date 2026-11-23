# Logarithmic Gaussian fitted to composite data (Methods, Composite metrics, p. 9), on Young's modulus
# (Fig. 4f): C(E) = A exp(-(log10 E - m)^2 / (2 s^2)), E_opt = 10^m. Same fit as gaussian_optimum_ks,
# repeated here so that a run depends only on this file.
import math

import numpy as np
from scipy.optimize import curve_fit


def run(inputs, settings):
    pts = [(math.log10(x), y) for x, y in zip(inputs["C"]["x"], inputs["C"]["y"]) if x is not None and y is not None and x > 0]
    u = np.array([p[0] for p in pts])
    c = np.array([p[1] for p in pts])
    m0 = float(u[int(np.argmax(c))])
    if settings.get("fit_amplitude", False):
        f = lambda uu, m, s, a: a * np.exp(-((uu - m) ** 2) / (2 * s * s))
        p, _ = curve_fit(f, u, c, p0=[m0, 1.0, 1.0], maxfev=20000)
    else:
        f = lambda uu, m, s: np.exp(-((uu - m) ** 2) / (2 * s * s))
        p, _ = curve_fit(f, u, c, p0=[m0, 1.0], maxfev=20000)
    return {"E_opt": 10.0 ** float(p[0])}
