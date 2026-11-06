import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    R, C, Zc = inputs["R"], inputs["C"], inputs["Zc"]
    z = Zc + R / (1 + 1j * w * R * C)
    return {"Zmod": abs(z), "phase": math.degrees(cmath.phase(z))}
