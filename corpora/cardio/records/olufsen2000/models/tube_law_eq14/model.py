# Eq. 14 (p. 5): p - p0 = (4/3)(E h/r0)(1 - sqrt(A0/A)), A0 = pi r0^2. CGS units.
import math


def run(inputs, settings):
    A0 = math.pi * inputs["r0"] ** 2
    stiff = 4.0 / 3.0 * inputs["E"] * inputs["h"] / inputs["r0"]
    return {"p": inputs["p0"] + stiff * (1.0 - math.sqrt(A0 / inputs["A"]))}


def symbolic():
    import sympy as sp
    A, r0, E, h, p0 = sp.symbols("A r0 E h p0", positive=True)
    A0 = sp.pi * r0 ** 2
    return {"p": p0 + sp.Rational(4, 3) * E * h / r0 * (1 - sp.sqrt(A0 / A))}
