# Lateral surface of a cylinder, pi l d; d converted nm -> um.
import math


def run(inputs, settings):
    return {"A": math.pi * inputs["l"] * inputs["d"] * 1e-3}


def symbolic():
    import sympy as sp
    l, d = sp.symbols("l d", positive=True)
    return {"A": sp.pi * l * d * sp.Rational(1, 1000)}
