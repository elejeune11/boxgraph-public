import math


def run(inputs, settings):
    s0, G, tau, t = inputs["sigma0"], inputs["G"], inputs["tau"], inputs["t"]
    return {"eps": s0 / (2.0 * G) * (math.exp(t / tau) - 1.0)}


def symbolic():
    import sympy as sp
    s0, G, tau, t = sp.symbols("sigma0 G tau t", positive=True)
    return {"eps": s0 / (2 * G) * (sp.exp(t / tau) - 1)}
