import math


def run(inputs, settings):
    return {"Cf": 1.75 / math.sqrt(150.0 * inputs["eps"] ** 3)}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    return {"Cf": sp.Rational(175, 100) / sp.sqrt(150 * eps**3)}
