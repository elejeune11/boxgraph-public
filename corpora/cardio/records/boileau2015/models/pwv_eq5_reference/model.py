# Eq. 5 (p. 4) evaluated at A = Ad: c = sqrt(beta / (2 rho Ad)) Ad^(1/4); beta from Eq. 3. SI units.
import math


def run(inputs, settings):
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    Ad = inputs["Ad"]
    return {"c": math.sqrt(beta / (2.0 * inputs["rho"] * Ad)) * Ad ** 0.25}


def symbolic():
    import sympy as sp
    Ad, E, h, rho = sp.symbols("Ad E h rho", positive=True)
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    return {"c": sp.sqrt(beta / (2 * rho * Ad)) * Ad ** sp.Rational(1, 4)}
