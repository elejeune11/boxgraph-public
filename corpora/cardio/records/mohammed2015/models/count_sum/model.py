def run(inputs, settings):
    return {"n": inputs["a"] + inputs["b"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("a b", nonnegative=True)
    return {"n": a + b}
