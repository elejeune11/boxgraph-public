# E = 2 (1 + eta) kappa / (pi r). (nN/um) / um = 1e-3 N/m / 1e-6 m = 1e3 Pa = 1 kPa.
import math


def run(inputs, settings):
    return {"E": 2.0 * (1.0 + inputs["eta"]) * inputs["k"] / (math.pi * inputs["r"])}


def symbolic():
    import sympy as sp
    k, r, eta = sp.symbols("k r eta", positive=True)
    return {"E": 2 * (1 + eta) * k / (sp.pi * r)}
