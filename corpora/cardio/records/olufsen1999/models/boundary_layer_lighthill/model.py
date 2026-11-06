# delta = (nu/omega)^(1/2) with omega = 2 pi / T, the first (dimensionally consistent) form printed.
# The second printed form, [nu T/(2 pi)]^2, has dimension length^4 and is recorded as a question.
import math


def run(inputs, settings):
    omega = 2 * math.pi / inputs["T"]
    return {"delta": math.sqrt(inputs["nu"] / omega)}


def symbolic():
    import sympy as sp
    nu, T = sp.symbols("nu T", positive=True)
    return {"delta": sp.sqrt(nu * T / (2 * sp.pi))}
