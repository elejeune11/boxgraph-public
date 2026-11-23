# Determinant of the Jacobian as printed in Eq. 20 (p. 5), evaluated at the stable fixed point (Eqs. 10, 15).
import math

from scipy.optimize import brentq


def _fixed(p):
    nm0 = p["w"] * p["Nm"] / (p["w"] + math.exp(p["fs"] / p["fd"]))
    A = nm0 * p["fs"] - p["F"]
    if A <= 0:
        raise ValueError("nm0 fs - F <= 0: only the trivial fixed point")
    a, r, Nc = A / p["Fb"], p["koff"] / p["kon"], p["Nc"]
    nstar = brentq(lambda n: 1 + r * math.exp(min(a / n, 700.0)) * (1 - a / n), a / 700.0, a, xtol=1e-14)
    g = lambda n: n + r * n * math.exp(min(a / n, 700.0)) - Nc  # noqa: E731
    if g(nstar) > 0:
        raise ValueError("Nc < Nc,min: no fixed point (region N)")
    return nm0, brentq(g, nstar, Nc, xtol=1e-14)


def run(inputs, settings):
    p = inputs
    nm, nc = _fixed(p)
    Fb, fs, F = p["Fb"], p["fs"], p["F"]
    det = (-(p["vu"] * p["kc"] * p["km"] * p["ks"]) / (Fb * fs) * math.exp(-F / (nc * Fb))
           * (math.exp(fs / p["fd"]) + p["w"])
           * (p["koff"] * math.exp(nm * fs / (nc * Fb)) * (F + nc * Fb - nm * fs)
              + math.exp(F / (nc * Fb)) * nc * Fb * p["kon"]))
    return {"det": det}
