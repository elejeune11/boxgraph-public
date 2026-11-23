# kappa = pi E r / (2 (1 + eta)). Pa * um = 1e-6 N/m = 1e-3 nN/um.
import math


def run(inputs, settings):
    return {"k": math.pi * inputs["E"] * inputs["r"] * 1e-3 / (2.0 * (1.0 + inputs["eta"]))}


def symbolic():
    import sympy as sp
    E, r, eta = sp.symbols("E r eta", positive=True)
    return {"k": sp.pi * E * r * sp.Rational(1, 1000) / (2 * (1 + eta))}
