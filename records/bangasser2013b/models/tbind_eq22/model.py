# Eq. 22: tbind = (ln(nc) + c)/kon, c = Euler's constant. kon 1/s -> s.
import math

EULER_GAMMA = 0.5772156649015329


def run(inputs, settings):
    return {"tbind": (math.log(inputs["nc"]) + EULER_GAMMA) / inputs["kon"]}


def symbolic():
    import sympy as sp
    nc, kon = sp.symbols("nc kon", positive=True)
    return {"tbind": (sp.log(nc) + sp.EulerGamma) / kon}
