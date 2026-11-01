import math


def run(inputs, settings):
    # RAB nm -> cm is 1e-7; rates are per molecule (cm^3/s), Kd_s in nm^3 per molecule
    D = inputs["DsA"] + inputs["DsB"]
    R = inputs["RAB"] * 1e-7
    return {
        "d_plus_s": 4 * math.pi * D * R,
        "d_minus_s": 3 * D / R**2,
        "Kd_s": 4 * math.pi / 3 * inputs["RAB"] ** 3,
    }


def symbolic():
    import sympy as sp
    DsA, DsB, RAB = sp.symbols("DsA DsB RAB", positive=True)
    R = RAB * sp.Rational(1, 10**7)
    return {
        "d_plus_s": 4 * sp.pi * (DsA + DsB) * R,
        "d_minus_s": 3 * (DsA + DsB) / R**2,
        "Kd_s": 4 * sp.pi / 3 * RAB**3,
    }
