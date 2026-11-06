import math


def run(inputs, settings):
    return {"P": inputs["P0"] * math.exp(-inputs["t"] / (inputs["R"] * inputs["C"])) + inputs["Pi"]}


def symbolic():
    import sympy as sp
    P0, Pi, R, C, t = sp.symbols("P0 Pi R C t", positive=True)
    return {"P": P0 * sp.exp(-t / (R * C)) + Pi}
