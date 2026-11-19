import math


def run(inputs, settings):
    return {"n": math.log10(inputs["k_max"] / inputs["k_min"])}


def symbolic():
    import sympy as sp

    k_min, k_max = sp.symbols("k_min k_max", positive=True)
    return {"n": sp.log(k_max / k_min, 10)}
