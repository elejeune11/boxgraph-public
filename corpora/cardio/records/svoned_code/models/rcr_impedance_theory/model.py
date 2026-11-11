# The RCR map of the code's theory notes (docs/source/content/theory.rst, lines 263-267) for a periodic
# flow: Q = p/R - 1/(R^2 C) int p exp(-alpha (t - tau)) dtau with alpha = (R + Rd)/(R Rd C). At the
# frequency f the admittance is 1/R - 1/(R^2 C (i omega + alpha)), whose inverse is the impedance
# R + Rd/(1 + i omega Rd C). Our code.
import cmath
import math


def run(inputs, settings):
    R, Rd, C = inputs["Rc"], inputs["Rd"], inputs["C"]
    w = 2 * math.pi * inputs["f"]
    alpha = (R + Rd) / (R * Rd * C)
    Y = 1.0 / R - 1.0 / (R * R * C * (1j * w + alpha))
    Z = 1.0 / Y
    return {"modulus": abs(Z), "phase": math.degrees(cmath.phase(Z))}
