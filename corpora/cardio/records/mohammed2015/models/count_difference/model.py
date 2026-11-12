def run(inputs, settings):
    return {"m": inputs["n"] - inputs["k"]}


def symbolic():
    import sympy as sp
    n, k = sp.symbols("n k", nonnegative=True)
    return {"m": n - k}
