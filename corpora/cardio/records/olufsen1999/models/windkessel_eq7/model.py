"""Eq. 7: Z = (R1 + R2 + i w CT R1 R2)/(1 + i w CT R2). Units g/s/cm^4, cm^4 s^2/g, 1/s."""
import cmath
import math


def run(inputs, settings):
    r1, r2, ct, w = inputs["R1"], inputs["R2"], inputs["CT"], inputs["omega"]
    z = (r1 + r2 + 1j * w * ct * r1 * r2) / (1 + 1j * w * ct * r2)
    return {"Zmod": abs(z), "Zphase": math.degrees(cmath.phase(z))}
