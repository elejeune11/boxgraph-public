# Rigid-substrate steady state of the mean-field model (SI Eqs. S31-S36).
# The steady density (S24/S33) is P(x) = P(0+) exp(-(e^{Fx} - 1)/(F ve)) for x > 0. With
# s = F x and z = 1/(F ve):
#   beta  = int_0^oo exp(-(e^{Fx}-1) z) dx       = (1/F)   int_0^oo exp(-(e^s - 1) z) ds
#   alpha = int_0^oo x exp(-(e^{Fx}-1) z) dx     = (1/F^2) int_0^oo s exp(-(e^s - 1) z) ds
# and ve solves S34: ve^2 + (tau beta - omega/F) ve + (tau omega/F)(alpha - beta) = 0, with
# ve in (0, omega/F]. The roots are bracketed on a log grid of n_scan points; when there are
# several, `root` picks one (smallest_ve: the highest-traction branch).
import math

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq


def _moments(F, ve):
    z = 1.0 / (F * ve)
    smax = math.log(1.0 + 800.0 / z)            # beyond, exp(-(e^s - 1) z) < e^-800
    w = lambda s: math.exp(-math.expm1(s) * z)
    b = quad(w, 0.0, smax, limit=500)[0] / F
    a = quad(lambda s: s * w(s), 0.0, smax, limit=500)[0] / F ** 2
    return a, b


def run(inputs, settings):
    F, tau, om = inputs["F"], inputs["tau"], inputs["omega"]

    def g(ve):
        a, b = _moments(F, ve)
        return ve * ve + (tau * b - om / F) * ve + tau * om / F * (a - b)

    top = om / F
    xs = np.geomspace(top * 1e-9, top * (1 - 1e-9), int(settings.get("n_scan", 400)))
    gs = [g(x) for x in xs]
    roots = [brentq(g, xs[k], xs[k + 1], xtol=1e-14 * top, rtol=1e-12)
             for k in range(len(xs) - 1) if gs[k] == 0 or gs[k] * gs[k + 1] < 0]
    if not roots:
        return {"T": float("nan"), "nb": float("nan"), "ve": float("nan")}
    ve = min(roots) if settings.get("root", "smallest_ve") == "smallest_ve" else max(roots)
    a, b = _moments(F, ve)
    nb = tau * b / (tau * b + ve)
    return {"T": F * nb * a / b, "nb": nb, "ve": ve}
