def run(inputs, settings):
    return {"r": 100.0 * (inputs["a"] - inputs["n"]) / inputs["a"]}  # in percent


def symbolic():
    import sympy as sp
    a, n = sp.symbols("a n", positive=True)
    return {"r": 100 * (a - n) / a}
