# Eq. B28 (p. 7), also printed on p. 2.
import math


def run(inputs, settings):
    g = inputs["gb"]
    num = g**4 - 2 * g**2 + math.sqrt(5 * g**8 + 8 * g**6 + 2 * g**4 + 1) + 1
    return {"eta_b": num / (g**6 + 3 * g**4 - g**2 + 1)}


def symbolic():
    import sympy as sp
    g = sp.symbols("gb", positive=True)
    num = g**4 - 2 * g**2 + sp.sqrt(5 * g**8 + 8 * g**6 + 2 * g**4 + 1) + 1
    return {"eta_b": num / (g**6 + 3 * g**4 - g**2 + 1)}
