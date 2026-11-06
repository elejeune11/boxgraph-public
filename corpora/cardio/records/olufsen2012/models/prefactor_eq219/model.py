import math


def run(inputs, settings):
    return {"c": math.exp(inputs["b"])}


def symbolic():
    import sympy as sp
    b = sp.symbols("b", real=True)
    return {"c": sp.exp(b)}
