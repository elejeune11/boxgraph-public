import math


def run(inputs, settings):
    # d in um -> mm (1e-3); n per mm^2: area fraction = n * pi d^2 / 4 (dimensionless)
    d_mm = inputs["d"] * 1e-3
    return {"phi_c": inputs["n"] * math.pi * d_mm**2 / 4.0}


def symbolic():
    import sympy as sp
    d, n = sp.symbols("d n", positive=True)
    return {"phi_c": n * sp.pi * (d * sp.Rational(1, 1000)) ** 2 / 4}
