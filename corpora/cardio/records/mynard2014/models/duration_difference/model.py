def run(inputs, settings):
    return {"d": inputs["a"] - inputs["b"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("a b", real=True)
    return {"d": a - b}
