# B = T lambda^4 / (16 pi^2 L^2). SI units.
import math


def run(inputs, settings):
    return {"B": inputs["T"] * inputs["lam"] ** 4 / (16.0 * math.pi**2 * inputs["L"] ** 2)}


def symbolic():
    import sympy as sp
    T, lam, L = sp.symbols("T lam L", positive=True)
    return {"B": T * lam**4 / (16 * sp.pi**2 * L**2)}
