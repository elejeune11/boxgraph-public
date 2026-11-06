import math


def run(inputs, settings):
    return {"N": inputs["A_total"] / (math.pi * (inputs["d"] / 2) ** 2)}


def symbolic():
    import sympy as sp
    A, d = sp.symbols("A_total d", positive=True)
    return {"N": A / (sp.pi * (d / 2) ** 2)}
