import math


def run(inputs, settings):
    mu = inputs["eta"] * inputs["h"]
    return {"X": math.sqrt(2 * mu * inputs["V0"] / inputs["Tbar"])}


def symbolic():
    import sympy as sp
    eta, h, V0, Tbar = sp.symbols("eta h V0 Tbar", positive=True)
    return {"X": sp.sqrt(2 * eta * h * V0 / Tbar)}
