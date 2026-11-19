# Fig. 1(b) dashed line, as labelled: l/a = (8 pi^3 eta / 3)^(1/3) (= 2 pi (eta/3)^(1/3)).
import math


def run(inputs, settings):
    return {"l_over_a": (8.0 * math.pi**3 * inputs["eta"] / 3.0) ** (1.0 / 3.0)}


def symbolic():
    import sympy as sp
    eta = sp.symbols("eta", positive=True)
    return {"l_over_a": (8 * sp.pi**3 * eta / 3) ** sp.Rational(1, 3)}
