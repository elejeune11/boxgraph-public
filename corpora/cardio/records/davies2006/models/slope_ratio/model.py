def run(inputs, settings):
    return {"r": inputs["a"] / inputs["b"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("a b", positive=True)
    return {"r": a / b}
