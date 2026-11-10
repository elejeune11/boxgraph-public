# Diameter of a circular cross-section of area A: d = sqrt(4 A / pi). Port units: mm^2, mm.
import math


def run(inputs, settings):
    return {"d": math.sqrt(4.0 * inputs["A"] / math.pi)}


def symbolic():
    import sympy as sp
    A = sp.symbols("A", positive=True)
    return {"d": sp.sqrt(4 * A / sp.pi)}
