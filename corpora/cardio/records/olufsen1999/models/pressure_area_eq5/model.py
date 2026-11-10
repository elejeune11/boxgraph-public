# Eq. 5 as printed, p - p0 = (4/3)(Eh/r0)(1 - sqrt(A0/A)), with A0 = pi r0^2 (p. 3) and
# Eh/r0 = k1 exp(k2 r0) + k3 (Eq. 6). CGS: g/s^2/cm = dyn/cm^2.
import math


def run(inputs, settings):
    r0 = inputs["r0"]
    ehr0 = inputs["k1"] * math.exp(inputs["k2"] * r0) + inputs["k3"]
    a0 = math.pi * r0 ** 2
    return {"p": inputs["p0"] + 4.0 / 3.0 * ehr0 * (1.0 - math.sqrt(a0 / inputs["A"]))}


def symbolic():
    import sympy as sp
    k1, k3, r0, A = sp.symbols("k1 k3 r0 A", positive=True)
    k2, p0 = sp.symbols("k2 p0", real=True)
    ehr0 = k1 * sp.exp(k2 * r0) + k3
    return {"p": p0 + sp.Rational(4, 3) * ehr0 * (1 - sp.sqrt(sp.pi * r0 ** 2 / A))}
