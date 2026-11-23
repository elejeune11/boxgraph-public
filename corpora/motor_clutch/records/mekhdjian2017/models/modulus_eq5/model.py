# Supplemental Eq. 5: E = 9 ksub / (4 pi r_adh). pN/nm / nm = 1e-12 N / 1e-18 m^2 = 1e6 Pa = 1e3 kPa.
import math


def run(inputs, settings):
    return {"E": 9 * inputs["ksub"] / (4 * math.pi * inputs["r_adh"]) * 1e3}


def symbolic():
    import sympy as sp
    ksub, r_adh = sp.symbols("ksub r_adh", positive=True)
    return {"E": 9 * ksub / (4 * sp.pi * r_adh) * 1000}
