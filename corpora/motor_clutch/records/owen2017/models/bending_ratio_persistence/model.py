# kappa = kappa_b / (kappa_s l^2), kappa_b = kB T Lp (definition of the persistence length of a
# semiflexible polymer), kappa_s = Ef * pi d^2 / 4. All converted to SI.
import math

KB = 1.380649e-23  # J/K


def run(inputs, settings):
    kb = KB * inputs["T"] * inputs["Lp"] * 1e-6                       # J m
    ks = inputs["Ef"] * 1e6 * math.pi * (inputs["d"] * 1e-9) ** 2 / 4  # N
    l = inputs["l"] * 1e-6                                             # m
    return {"kappa": kb / (ks * l * l)}


def symbolic():
    import sympy as sp
    Lp, T, Ef, d, l = sp.symbols("Lp T Ef d l", positive=True)
    kb = sp.Float(KB) * T * Lp * sp.Rational(1, 10**6)
    ks = Ef * 10**6 * sp.pi * (d * sp.Rational(1, 10**9)) ** 2 / 4
    return {"kappa": kb / (ks * (l * sp.Rational(1, 10**6)) ** 2)}
