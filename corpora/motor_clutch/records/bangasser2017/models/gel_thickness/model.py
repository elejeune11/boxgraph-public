# h = V / (pi (d/2)^2). V in uL (= mm^3), d in mm, h in um.
import math


def run(inputs, settings):
    h_mm = inputs["V"] / (math.pi * (inputs["d"] / 2.0) ** 2)
    return {"h": h_mm * 1000.0}


def symbolic():
    import sympy as sp
    V, d = sp.symbols("V d", positive=True)
    return {"h": 1000 * V / (sp.pi * (d / 2) ** 2)}
