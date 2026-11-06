import cmath
import math


def run(inputs, settings):
    w = 2 * math.pi * inputs["f"]
    z = (inputs["a"] + 1j * w * inputs["b"]) / (1 + 1j * w * inputs["c"])
    return {"Zmod": abs(z), "phase": math.degrees(cmath.phase(z))}
