def run(inputs, settings):
    return {"d": inputs["n"] / inputs["A"]}


def symbolic():
    import sympy as sp
    n, A = sp.symbols("n A", positive=True)
    return {"d": n / A}
