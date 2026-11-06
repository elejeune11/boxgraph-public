# Eq. 15 (p. 15), as the ratio Ppeak,visc(x) / Ppeak,inv. Ppeak,inv is the inlet peak, since the
# inviscid peak keeps its amplitude (p. 15), so the ratio is what Fig. 2 plots as P/Ppeak. SI units.
import math


def run(inputs, settings):
    k = (inputs["zeta"] + 2.0) * math.pi * inputs["mu"] / (inputs["rho"] * inputs["c0"] * inputs["A0"])
    return {"ratio": math.exp(-k * inputs["x"])}


def symbolic():
    import sympy as sp
    zeta, mu, rho, c0, A0, x = sp.symbols("zeta mu rho c0 A0 x", positive=True)
    return {"ratio": sp.exp(-(zeta + 2) * sp.pi * mu * x / (rho * c0 * A0))}
