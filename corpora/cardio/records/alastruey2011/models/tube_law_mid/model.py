import math


def run(inputs, settings):
    xi = settings["xi"]
    r0 = inputs["r0in"] + (inputs["r0out"] - inputs["r0in"]) * xi
    c0 = inputs["c0in"] + (inputs["c0out"] - inputs["c0in"]) * xi
    A0 = math.pi * r0 ** 2
    beta = 2.0 * inputs["rho"] * c0 ** 2 * math.sqrt(A0)
    return {"A": (math.sqrt(A0) + (inputs["P"] - inputs["Pext"]) * A0 / beta) ** 2}


def symbolic():
    import sympy as sp
    P, r0in, r0out, c0in, c0out, rho, Pext = sp.symbols("P r0in r0out c0in c0out rho Pext", real=True)
    xi = sp.Rational(1, 2)
    r0 = r0in + (r0out - r0in) * xi
    c0 = c0in + (c0out - c0in) * xi
    A0 = sp.pi * r0 ** 2
    beta = 2 * rho * c0 ** 2 * sp.sqrt(A0)
    return {"A": (sp.sqrt(A0) + (P - Pext) * A0 / beta) ** 2}
