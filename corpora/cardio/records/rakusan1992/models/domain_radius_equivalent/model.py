# Radius of the circle with the same area as a capillary domain.
import math


def run(inputs, settings):
    return {"r": math.sqrt(inputs["A"] / math.pi)}


def symbolic():
    import sympy as sp
    A = sp.symbols("A", positive=True)
    return {"r": sp.sqrt(A / sp.pi)}
