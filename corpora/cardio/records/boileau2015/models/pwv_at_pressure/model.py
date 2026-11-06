# Eq. 3 (p. 3) with Pext = 0 gives sqrt(A) = sqrt(Ad) + (P - Pd) Ad / beta; Eq. 5 (p. 4) then gives
# c = sqrt(beta / (2 rho Ad)) A^(1/4). SI units.
import math


def run(inputs, settings):
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    Ad = inputs["Ad"]
    sqrtA = math.sqrt(Ad) + (inputs["P"] - inputs["Pd"]) * Ad / beta
    return {"c": math.sqrt(beta / (2.0 * inputs["rho"] * Ad)) * math.sqrt(sqrtA)}


def symbolic():
    import sympy as sp
    P, Pd, Ad, E, h, rho = sp.symbols("P Pd Ad E h rho", positive=True)
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    sqrtA = sp.sqrt(Ad) + (P - Pd) * Ad / beta
    return {"c": sp.sqrt(beta / (2 * rho * Ad)) * sp.sqrt(sqrtA)}
