# The paper says R1 "is equal to the characteristic impedance of the end point" (p. 5) without
# writing it. The characteristic impedance of a 1D segment is Z0 = rho c / A; it is evaluated here at
# the reference state A = Ad, with c from Eq. 5 and beta from Eq. 3 (reader's reading). SI units.
import math


def run(inputs, settings):
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    Ad = inputs["Ad"]
    c = math.sqrt(beta / (2.0 * inputs["rho"] * Ad)) * Ad ** 0.25
    return {"R1": inputs["rho"] * c / Ad}


def symbolic():
    import sympy as sp
    Ad, E, h, rho = sp.symbols("Ad E h rho", positive=True)
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    c = sp.sqrt(beta / (2 * rho * Ad)) * Ad ** sp.Rational(1, 4)
    return {"R1": rho * c / Ad}
