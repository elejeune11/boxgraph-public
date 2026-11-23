# Determinant of the Jacobian of the right-hand side of Eq. 18 (= A1), p. 5, at the stable fixed point
# (Eqs. 9-15), by central finite differences (relative step `h`). Independent of the printed matrix A3.
import math

import numpy as np
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
    nc0 = brentq(g, nstar, Nc, xtol=1e-14)
    xs0 = A / p["ks"]
    return np.array([nm0, nc0, xs0 + A / (nc0 * p["kc"]), p["fs"] / p["km"], xs0])


def rhs(s, p):
    nm, nc, xo, y, xs = s
    xc = xo - xs
    f3 = nm * p["km"] * y - nc * p["kc"] * xc - p["F"]
    return np.array([
        p["w"] * (p["Nm"] - nm) - nm * math.exp(p["km"] * y / p["fd"]),
        p["kon"] * (p["Nc"] - nc) - p["koff"] * nc * math.exp(p["kc"] * xc / p["Fb"]),
        f3,
        p["vu"] * (1 - p["km"] * y / p["fs"]) - f3,
        (nc * p["kc"] * xc - p["ks"] * xs) / p["g"],  # (Gamma/gamma)(...)
    ])


def run(inputs, settings):
    s0 = _fixed(inputs)
    h = float(settings.get("h", 1e-6))
    J = np.empty((5, 5))
    for j in range(5):
        d = h * max(1.0, abs(s0[j]))
        e = np.zeros(5)
        e[j] = d
        J[:, j] = (rhs(s0 + e, inputs) - rhs(s0 - e, inputs)) / (2 * d)
    return {"det": float(np.linalg.det(J))}
