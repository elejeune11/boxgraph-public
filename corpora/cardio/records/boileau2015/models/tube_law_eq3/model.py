# Eq. 3 (p. 3): P - Pext = Pd + beta/Ad (sqrt(A) - sqrt(Ad)), beta = (4/3) sqrt(pi) E h. SI units.
import math


def run(inputs, settings):
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    Ad = inputs["Ad"]
    return {"P": inputs["Pext"] + inputs["Pd"] + beta / Ad * (math.sqrt(inputs["A"]) - math.sqrt(Ad))}


def symbolic():
    import sympy as sp
    A, Ad, Pd, E, h, Pext = sp.symbols("A Ad Pd E h Pext", positive=True)
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    return {"P": Pext + Pd + beta / Ad * (sp.sqrt(A) - sp.sqrt(Ad))}
