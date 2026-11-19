# The paper says only that B and "the in-plane modulus" give the thickness. With B = E t^3/[12(1 - nu^2)]
# (p. 2) and the in-plane modulus Y = E t: t = sqrt(12 (1 - nu^2) B / Y). SI units.
import math


def run(inputs, settings):
    return {"t": math.sqrt(12.0 * (1.0 - inputs["nu"] ** 2) * inputs["B"] / inputs["Y"])}


def symbolic():
    import sympy as sp
    B, Y, nu = sp.symbols("B Y nu", positive=True)
    return {"t": sp.sqrt(12 * (1 - nu**2) * B / Y)}
