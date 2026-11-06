import math


def run(inputs, settings):
    return {"gen": math.log2(inputs["N"] / inputs["n_sub"])}


def symbolic():
    import sympy as sp
    N, n = sp.symbols("N n_sub", positive=True)
    return {"gen": sp.log(N / n, 2)}
