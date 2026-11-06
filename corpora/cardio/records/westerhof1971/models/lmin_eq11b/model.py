import math


def run(inputs, settings):
    return {"l": math.sqrt(inputs["k"] * inputs["dP"])}


def symbolic():
    import sympy as sp
    k, dP = sp.symbols("k dP", positive=True)
    return {"l": sp.sqrt(k * dP)}
