import math


def run(inputs, settings):
    a = (2 * math.pi * inputs["nu"]) ** 2 * inputs["A"]  # mm/s^2
    return {"a": a, "F": inputs["m"] * a * 0.1}  # g * mm/s^2 -> dyne is 0.1


def symbolic():
    import sympy as sp
    nu, A, m = sp.symbols("nu A m", positive=True)
    a = (2 * sp.pi * nu) ** 2 * A
    return {"a": a, "F": m * a * sp.Rational(1, 10)}
