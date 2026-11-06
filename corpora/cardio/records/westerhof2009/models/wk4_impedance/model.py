import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    R, C, Zc, L = inputs["R"], inputs["C"], inputs["Zc"], inputs["L"]
    jwL = 1j * w * L
    # Zc parallel L; at f = 0 the inductive branch shorts Zc
    zp = 0j if jwL == 0 else Zc * jwL / (Zc + jwL)
    z = zp + R / (1 + 1j * w * R * C)
    return {"Zmod": abs(z), "phase": math.degrees(cmath.phase(z))}
