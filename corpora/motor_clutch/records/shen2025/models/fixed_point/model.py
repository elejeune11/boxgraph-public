# Fixed point of Eq. 6 (Eqs. 9-15, p. 4). Eq. 15 has two roots for Nc > Nc,min (p. 4); the paper studies the
# larger one, the stable branch (p. 5). The root is bracketed between the minimum of g (Eq. 17 = 0) and Nc.
import math

from scipy.optimize import brentq


def _nc_root(Nc, A, r, Fb):
    if A <= 0:  # case 2 (p. 5): only the trivial solution
        raise ValueError("nm0 fs - F <= 0: Eq. 15 has only the trivial solution")
    a = A / Fb

    def g(n):
        return n + r * n * math.exp(min(a / n, 700.0)) - Nc

    def gp(n):
        return 1 + r * math.exp(min(a / n, 700.0)) * (1 - a / n)

    nstar = brentq(gp, a / 700.0, a, xtol=1e-14)
    if g(nstar) > 0:
        raise ValueError("Nc < Nc,min: no fixed point (region N)")
    return brentq(g, nstar, Nc, xtol=1e-14)


def run(inputs, settings):
    p = inputs
    nm0 = p["w"] * p["Nm"] / (p["w"] + math.exp(p["fs"] / p["fd"]))
    A = nm0 * p["fs"] - p["F"]
    nc0 = _nc_root(p["Nc"], A, p["koff"] / p["kon"], p["Fb"])
    xs0 = A / p["ks"]
    xc0 = A / (nc0 * p["kc"])
    return {"nm0": nm0, "nc0": nc0, "y0": p["fs"] / p["km"], "xs0": xs0,
            "xo0": (p["ks"] / (nc0 * p["kc"]) + 1) * A / p["ks"], "xc0": xc0}
