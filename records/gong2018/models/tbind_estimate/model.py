# tbind = ln(Nc)/ron.  Ports: Nc 1, ron 1/s -> tbind s.
import math


def run(inputs, settings):
    return {"tbind": math.log(inputs["Nc"]) / inputs["ron"]}


def symbolic():
    import sympy as sp
    Nc, ron = sp.symbols("Nc ron", positive=True)
    return {"tbind": sp.log(Nc) / ron}
