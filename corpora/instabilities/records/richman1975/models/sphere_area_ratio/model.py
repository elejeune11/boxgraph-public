import math


def run(inputs, settings):
    R, t = inputs["R"], inputs["t"]
    return {"ratio": (4 * math.pi * R**2) / (4 * math.pi * (R - t) ** 2)}


def symbolic():
    import sympy as sp
    R, t = sp.symbols("R t", positive=True)
    return {"ratio": (4 * sp.pi * R**2) / (4 * sp.pi * (R - t) ** 2)}
