# Eq. 3.5: Delta beta^(c) / (d/delta) = 1 / (2 sqrt2), the same at every Lambda.
import math


def run(inputs, settings):
    return {"Bc": 1.0 / (2.0 * math.sqrt(2.0)) + 0.0 * inputs["L"]}


def symbolic():
    import sympy as sp
    L = sp.symbols("L", positive=True)
    return {"Bc": 1 / (2 * sp.sqrt(2)) + 0 * L}
