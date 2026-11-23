# Saddle-node point (p. 5): g'(nc0) = 0 (Eq. 17) gives nc0 at the bifurcation, Nc,min = g(nc0) (Eq. 16).
# With u = A/(nc0 Fb), A = nm0 fs - F: g' = 0 is 1 + r e^u (1 - u) = 0, r = koff/kon, a root u > 1.
import math

from scipy.optimize import brentq


def run(inputs, settings):
    p = inputs
    nm0 = p["w"] * p["Nm"] / (p["w"] + math.exp(p["fs"] / p["fd"]))
    A = (1.0 - p["load"]) * nm0 * p["fs"]
    if A <= 0:
        raise ValueError("load >= nm0 fs: no bifurcation (case 2, p. 5)")
    r = p["koff"] / p["kon"]
    u = brentq(lambda u: 1 + r * math.exp(u) * (1 - u), 1.0, 700.0, xtol=1e-14)
    nc = A / (u * p["Fb"])
    return {"Nc_min": nc + r * nc * math.exp(u), "nc_bif": nc}
