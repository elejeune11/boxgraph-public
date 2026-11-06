import math


def run(inputs, settings):
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    A0 = math.pi * inputs["r0"] ** 2
    return {"c0": math.sqrt(beta / (2.0 * inputs["rho"] * math.sqrt(A0)))}


def symbolic():
    import sympy as sp
    E, h, r0, rho = sp.symbols("E h r0 rho", positive=True)
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    A0 = sp.pi * r0 ** 2
    return {"c0": sp.sqrt(beta / (2 * rho * sp.sqrt(A0)))}
