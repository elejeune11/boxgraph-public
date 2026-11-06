# Eqs. 11-12, as printed. Pa * nm^2 = 1e-18 N = 1e-6 pN.
import math


def run(inputs, settings):
    E, nu, U1, U2, L = (inputs[k] for k in ("E", "nu", "U1", "U2", "L"))
    return {
        "T": math.pi * E / (1.0 + nu) * (U1 * U2 * L / (U1 - U2)) * 1e-6,
        "delta": U2 * L / (U1 - U2),
    }


def symbolic():
    import sympy as sp
    E, nu, U1, U2, L = sp.symbols("E nu U1 U2 L")
    return {"T": sp.pi * E / (1 + nu) * (U1 * U2 * L / (U1 - U2)) * sp.Rational(1, 10**6),
            "delta": U2 * L / (U1 - U2)}
