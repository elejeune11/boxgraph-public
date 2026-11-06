"""Eq. 7 terminal windkessel for one harmonic: Z = R1 + R2/(1 + j w R2 CT). Units dyn*s/cm^5, cm^5/dyn, Hz."""
import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    r1 = inputs["R1r"] * inputs["RT"]
    r2 = inputs["RT"] - r1
    z = r1 + r2 / (1 + 1j * w * r2 * inputs["CT"])
    return {"mod": abs(z), "phase": math.degrees(cmath.phase(z))}
