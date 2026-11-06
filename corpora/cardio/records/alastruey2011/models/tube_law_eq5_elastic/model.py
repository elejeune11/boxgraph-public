# Eq. 5 (p. 2) with Gamma = 0: P = Pext + (beta/A0)(sqrt(A) - sqrt(A0)), beta = (4/3) sqrt(pi) E h,
# A0 = pi r0^2. SI units.
import math


def run(inputs, settings):
    A0 = math.pi * inputs["r0"] ** 2
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    return {"P": inputs["Pext"] + beta / A0 * (math.sqrt(inputs["A"]) - math.sqrt(A0))}


def symbolic():
    import sympy as sp
    A, r0, E, h, Pext = sp.symbols("A r0 E h Pext", positive=True)
    A0 = sp.pi * r0 ** 2
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    return {"P": Pext + beta / A0 * (sp.sqrt(A) - sp.sqrt(A0))}
