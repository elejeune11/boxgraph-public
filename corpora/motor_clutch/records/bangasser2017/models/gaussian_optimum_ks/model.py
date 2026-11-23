# Logarithmic Gaussian fitted to composite data (Methods, Composite metrics, p. 9):
#   C(K) = A exp(-(log10 K - m)^2 / (2 s^2)),  optimum K_opt = 10^m.
# The variance is not constrained (as printed). The amplitude is a setting: fixed at 1 (the fitted
# curves of Figs. 1g and 4f peak at 1) unless fit_amplitude is true. Least squares on C.
import math

import numpy as np
from scipy.optimize import curve_fit


def fit(xs, ys, fit_amplitude=False):
    pts = [(math.log10(x), y) for x, y in zip(xs, ys) if x is not None and y is not None and x > 0]
    u = np.array([p[0] for p in pts])
    c = np.array([p[1] for p in pts])
    m0 = float(u[int(np.argmax(c))])
    if fit_amplitude:
        f = lambda uu, m, s, a: a * np.exp(-((uu - m) ** 2) / (2 * s * s))
        p, _ = curve_fit(f, u, c, p0=[m0, 1.0, 1.0], maxfev=20000)
    else:
        f = lambda uu, m, s: np.exp(-((uu - m) ** 2) / (2 * s * s))
        p, _ = curve_fit(f, u, c, p0=[m0, 1.0], maxfev=20000)
    return float(p[0]), abs(float(p[1]))


def run(inputs, settings):
    m, s = fit(inputs["C"]["x"], inputs["C"]["y"], bool(settings.get("fit_amplitude", False)))
    return {"K_opt": 10.0 ** m}
