import math


def run(inputs, settings):
    z = inputs["zeta"]
    k = math.sqrt((1 - z) / (1 + z))             # Eq. 2.8
    return {"phi": (k * (1 + z) ** 2 - 1) / z}   # Eq. 4.8


def symbolic():
    import sympy as sp
    zeta = sp.symbols("zeta", positive=True)
    k = sp.sqrt((1 - zeta) / (1 + zeta))
    return {"phi": (k * (1 + zeta) ** 2 - 1) / zeta}
