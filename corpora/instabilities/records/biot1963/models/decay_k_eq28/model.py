import math


def run(inputs, settings):
    z = inputs["zeta"]
    return {"k": math.sqrt((1 - z) / (1 + z))}


def symbolic():
    import sympy as sp
    zeta = sp.symbols("zeta", positive=True)
    return {"k": sp.sqrt((1 - zeta) / (1 + zeta))}
