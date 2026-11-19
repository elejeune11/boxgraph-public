import math


def run(inputs, settings):
    return {"rms_over_h": math.sqrt(0.5 * (inputs["N_over_Nc"] - 1))}


def symbolic():
    import sympy as sp
    r = sp.symbols("N_over_Nc", positive=True)
    return {"rms_over_h": sp.sqrt(sp.Rational(1, 2) * (r - 1))}
