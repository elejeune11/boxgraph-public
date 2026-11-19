# Eq. 1 as read from the page image (see question q_eq1_form): the factor 2 multiplies b2 inside the square.
import math


def run(inputs, settings):
    z = (inputs["s0"] - 0.5) / (2.0 * inputs["b2"])
    return {"Eb": 1.0 - inputs["b1"] * math.exp(-z * z)}


def symbolic():
    import sympy as sp

    b1, b2, s0 = sp.symbols("b1 b2 s0", positive=True)
    return {"Eb": 1 - b1 * sp.exp(-(((s0 - sp.Rational(1, 2)) / (2 * b2)) ** 2))}
