import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    R, C = inputs["R"], inputs["C"]
    z = R / (1 + 1j * w * R * C)
    return {"Zmod": abs(z), "phase": math.degrees(cmath.phase(z))}
