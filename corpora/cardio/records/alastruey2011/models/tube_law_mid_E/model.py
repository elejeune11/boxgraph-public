import math


def run(inputs, settings):
    xi = settings["xi"]
    r0 = inputs["r0in"] + (inputs["r0out"] - inputs["r0in"]) * xi
    A0 = math.pi * r0 ** 2
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    return {"A": (math.sqrt(A0) + (inputs["P"] - inputs["Pext"]) * A0 / beta) ** 2}


def symbolic():
    import sympy as sp
    P, r0in, r0out, E, h, Pext = sp.symbols("P r0in r0out E h Pext", real=True)
    xi = sp.Rational(1, 2)
    r0 = r0in + (r0out - r0in) * xi
    A0 = sp.pi * r0 ** 2
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    return {"A": (sp.sqrt(A0) + (P - Pext) * A0 / beta) ** 2}
