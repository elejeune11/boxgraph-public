# Eq. 17 (p. 21) for the wall thickness of a vessel of reference radius R0, then the characteristic
# impedance rho c / A at A = A0 = Ad = pi R0^2 (ADAN56 uses Ad = A0, Pd = P0, p. 21), with c from Eq. 5
# and beta from Eq. 3. This tests the p. 5 statement that R1 equals the end point's characteristic
# impedance on the ADAN56 terminals. SI units.
import math


def run(inputs, settings):
    R0 = inputs["R0"]
    h = R0 * (inputs["a"] * math.exp(inputs["b"] * R0) + inputs["c"] * math.exp(inputs["d"] * R0))
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * h
    A = math.pi * R0 ** 2
    c = math.sqrt(beta / (2.0 * inputs["rho"] * A)) * A ** 0.25
    return {"R1": inputs["rho"] * c / A}


def symbolic():
    import sympy as sp
    R0, E, rho, a, c_, = sp.symbols("R0 E rho a c", positive=True)
    b, d = sp.symbols("b d", real=True)
    h = R0 * (a * sp.exp(b * R0) + c_ * sp.exp(d * R0))
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    A = sp.pi * R0**2
    cw = sp.sqrt(beta / (2 * rho * A)) * A ** sp.Rational(1, 4)
    return {"R1": rho * cw / A}
