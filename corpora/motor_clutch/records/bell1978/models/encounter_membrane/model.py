import math


def run(inputs, settings):
    R = inputs["RAB"] * 1e-7  # nm -> cm
    return {
        "d_plus_m": 2 * math.pi * inputs["Dm_sum"],
        "d_minus_m": 2 * inputs["Dm_sum"] / R**2,
    }


def symbolic():
    import sympy as sp
    Dm_sum, RAB = sp.symbols("Dm_sum RAB", positive=True)
    R = RAB * sp.Rational(1, 10**7)
    return {"d_plus_m": 2 * sp.pi * Dm_sum, "d_minus_m": 2 * Dm_sum / R**2}
