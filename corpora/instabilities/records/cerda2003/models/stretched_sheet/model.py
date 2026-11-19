# lambda = (2 pi L t)^(1/2) / [3 (1 - nu^2) gamma]^(1/4)
# A = (nu L t)^(1/2) [16 gamma / (3 pi^2 (1 - nu^2))]^(1/4). SI units.
import math


def run(inputs, settings):
    L, t, nu, g = inputs["L"], inputs["t"], inputs["nu"], inputs["gamma"]
    lam = math.sqrt(2.0 * math.pi * L * t) / (3.0 * (1.0 - nu**2) * g) ** 0.25
    A = math.sqrt(nu * L * t) * (16.0 * g / (3.0 * math.pi**2 * (1.0 - nu**2))) ** 0.25
    return {"lam": lam, "A": A}


def symbolic():
    import sympy as sp
    L, t, nu, gamma = sp.symbols("L t nu gamma", positive=True)
    q = sp.Rational(1, 4)
    lam = sp.sqrt(2 * sp.pi * L * t) / (3 * (1 - nu**2) * gamma) ** q
    A = sp.sqrt(nu * L * t) * (16 * gamma / (3 * sp.pi**2 * (1 - nu**2))) ** q
    return {"lam": lam, "A": A}
