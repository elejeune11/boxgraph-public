import math


def run(inputs, settings):
    xc = inputs["n"] - inputs["n0"]
    return {"rho": (math.atan(inputs["alpha"] * (-xc)) + 1.5) / 3.0}


def symbolic():
    import sympy as sp
    alpha, n, n0 = sp.symbols("alpha n n0", real=True)
    return {"rho": (sp.atan(alpha * (-(n - n0))) + sp.Rational(3, 2)) / 3}
