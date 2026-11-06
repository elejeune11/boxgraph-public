import math


def run(inputs, settings):
    xi, g = inputs["xi"], inputs["gamma"]
    alpha = (1 + g ** (xi / 2)) ** (-1 / xi)
    return {"alpha": alpha, "beta": alpha * math.sqrt(g)}


def symbolic():
    import sympy as sp
    xi, gamma = sp.symbols("xi gamma", positive=True)
    alpha = (1 + gamma ** (xi / 2)) ** (-1 / xi)
    return {"alpha": alpha, "beta": alpha * sp.sqrt(gamma)}
