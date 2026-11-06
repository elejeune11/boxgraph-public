import math


def run(inputs, settings):
    r = inputs["d"] / 10.0 / 2.0  # mm -> cm, radius
    nu = inputs["mu"] / inputs["rho"]  # cm^2/s
    qf = 6.0 * nu / (r**2 * 2.0 * math.pi)  # Q * f, Hz
    return {"Q": qf / inputs["f"], "Qf": qf}


def symbolic():
    import sympy as sp
    d, mu, rho, f = sp.symbols("d mu rho f", positive=True)
    r = d / 20
    qf = 6 * (mu / rho) / (r**2 * 2 * sp.pi)
    return {"Q": qf / f, "Qf": qf}
