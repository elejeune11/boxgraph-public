# Eq. 4 as printed: a two-branch power law, defined for mu_f/mu_s >= 1.3.
import math


def run(inputs, settings):
    r = inputs["mu_ratio"]
    if r < 1.3:
        return {"eC": math.nan}  # outside the printed domain (creasing, Eq. 3)
    if r <= 16:
        return {"eC": 0.41 * r ** -0.59}
    return {"eC": 0.50 * r ** -0.66}


def symbolic():
    import sympy as sp
    mu_ratio = sp.symbols("mu_ratio", positive=True)
    return {"eC": sp.Piecewise((0.41 * mu_ratio ** -0.59, mu_ratio <= 16), (0.50 * mu_ratio ** -0.66, True))}
