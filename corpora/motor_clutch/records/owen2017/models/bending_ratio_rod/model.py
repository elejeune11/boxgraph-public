# kappa_b = Ef I with I = pi d^4 / 64 (solid circular rod), kappa_s = Ef pi d^2 / 4.
import math


def run(inputs, settings):
    Ef = inputs["Ef"] * 1e6
    d = inputs["d"] * 1e-9
    l = inputs["l"] * 1e-6
    kb = Ef * math.pi * d**4 / 64
    ks = Ef * math.pi * d**2 / 4
    return {"kappa": kb / (ks * l * l)}


def symbolic():
    import sympy as sp
    Ef, d, l = sp.symbols("Ef d l", positive=True)
    dd, ll = d * sp.Rational(1, 10**9), l * sp.Rational(1, 10**6)
    return {"kappa": (Ef * 10**6 * sp.pi * dd**4 / 64) / (Ef * 10**6 * sp.pi * dd**2 / 4 * ll**2)}
