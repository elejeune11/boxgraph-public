def run(inputs, settings):
    t2 = (inputs["b"] / inputs["se"]) ** 2
    return {"r2": t2 / (t2 + inputs["n"] - 2.0)}


def symbolic():
    import sympy as sp
    b, se, n = sp.symbols("b se n", positive=True)
    t2 = (b / se) ** 2
    return {"r2": t2 / (t2 + n - 2)}
