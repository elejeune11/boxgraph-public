# ZC = rho PWV / A, PWV from Eq. 22 (d in mm -> m/s), A = pi d^2/4 in m^2; R1 = ZC; output R1/RT.
import math


def run(inputs, settings):
    d_mm = inputs["d"]
    pwv = inputs["a2"] / d_mm ** inputs["b2"]
    area = math.pi * (d_mm * 1e-3) ** 2 / 4.0
    zc = inputs["rho"] * pwv / area
    return {"ratio": zc / inputs["RT"]}


def symbolic():
    import sympy as sp
    d, a2, b2, rho, RT = sp.symbols("d a2 b2 rho RT", positive=True)
    return {"ratio": rho * (a2 / d ** b2) / (sp.pi * (d / 1000) ** 2 / 4) / RT}
