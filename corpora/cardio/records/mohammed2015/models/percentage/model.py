def run(inputs, settings):
    return {"p": 100.0 * inputs["k"] / inputs["n"]}


def symbolic():
    import sympy as sp
    k, n = sp.symbols("k n", positive=True)
    return {"p": 100 * k / n}
