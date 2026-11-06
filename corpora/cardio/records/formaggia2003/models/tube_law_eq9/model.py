# Eqs. (9)-(10) (p. 5): P - Pext = beta (sqrt(A) - sqrt(A0))/A0, beta = E h0 sqrt(pi), A0 = pi R0^2 (Eq. 6).
# CGS units: cm, dyne.
import math


def run(inputs, settings):
    A0 = math.pi * inputs["R0"] ** 2
    beta = inputs["E"] * inputs["h0"] * math.sqrt(math.pi)
    return {"P": inputs["Pext"] + beta * (math.sqrt(inputs["A"]) - math.sqrt(A0)) / A0}


def symbolic():
    import sympy as sp
    A, R0, E, h0, Pext = sp.symbols("A R0 E h0 Pext", positive=True)
    A0 = sp.pi * R0 ** 2
    beta = E * h0 * sp.sqrt(sp.pi)
    return {"P": Pext + beta * (sp.sqrt(A) - sp.sqrt(A0)) / A0}
