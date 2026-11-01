# Eq. 23: tbind = ln(nc)/kon. kon 1/s -> s.
import math


def run(inputs, settings):
    return {"tbind": math.log(inputs["nc"]) / inputs["kon"]}


def symbolic():
    import sympy as sp
    nc, kon = sp.symbols("nc kon", positive=True)
    return {"tbind": sp.log(nc) / kon}
