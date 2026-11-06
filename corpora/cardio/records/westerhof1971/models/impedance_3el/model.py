import cmath
import math


def run(inputs, settings):
    # C in cm^4 s^2 / Mg = 1e-6 cm^4 s^2 / g (cgs)
    rc, rp, c, f = inputs["Rc"], inputs["Rp"], inputs["C"] * 1e-6, inputs["f"]
    w = 2 * math.pi * f
    z = rc + rp / (1 + 1j * w * rp * c)
    return {"modulus": abs(z), "phase": math.degrees(cmath.phase(z))}


def symbolic():
    import sympy as sp

    Rc, Rp, C, f = sp.symbols("Rc Rp C f", positive=True)
    w = 2 * sp.pi * f
    x = w * Rp * C * sp.Rational(1, 10**6)
    re = Rc + Rp / (1 + x**2)
    im = -Rp * x / (1 + x**2)
    return {"modulus": sp.sqrt(re**2 + im**2), "phase": sp.atan2(im, re) * 180 / sp.pi}
