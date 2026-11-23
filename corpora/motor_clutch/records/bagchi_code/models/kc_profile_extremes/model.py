# Our reconstruction: the drivers' Gaussian (lines 223-238) with the stiffness width.
import math


def run(inputs, settings):
    n = int(round(inputs["n"]))
    s = inputs["sigma"]
    uv = (n // 2) + 1
    vect = [(1 / (s * math.sqrt(2 * math.pi))) * math.exp(-(((i + 1 - uv) / s) ** 2.0) / 2) for i in range(n + 1)]
    return {"omega": max(vect), "delta": min(vect)}
