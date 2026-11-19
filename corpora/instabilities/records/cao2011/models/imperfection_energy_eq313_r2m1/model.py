# Eq. 3.13 with -mu lambda_1 (r^2 - 1) in front: with f(0) = (r - 1)/(r + 1) (Eq. 2.9),
# K = pi (r^2 - 1) f(0) = pi (r - 1)^2.
import math


def run(inputs, settings):
    r = inputs["r"]
    return {"K": math.pi * (r * r - 1.0) * (r - 1.0) / (r + 1.0)}


def symbolic():
    import sympy as sp
    r = sp.symbols("r", positive=True)
    return {"K": sp.pi * (r ** 2 - 1) * (r - 1) / (r + 1)}
