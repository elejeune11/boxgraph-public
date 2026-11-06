# Driver function e(t), Eq. 5 of Smith et al. 2004, with N = 1 (one Gaussian term).
import math


def run(inputs, settings):
    A, B, C, t = inputs["A"], inputs["B"], inputs["C"], inputs["t"]
    return {"e": A * math.exp(-B * (t - C) ** 2)}


def symbolic():
    import sympy as sp
    A, B, C = sp.symbols("A B C", positive=True)
    t = sp.symbols("t", real=True)
    return {"e": A * sp.exp(-B * (t - C) ** 2)}
