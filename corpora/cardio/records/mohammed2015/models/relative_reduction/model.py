def run(inputs, settings):
    a, b = inputs["a"], inputs["b"]
    return {"r": 100.0 * (a - b) / a}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("a b", positive=True)
    return {"r": 100 * (a - b) / a}
