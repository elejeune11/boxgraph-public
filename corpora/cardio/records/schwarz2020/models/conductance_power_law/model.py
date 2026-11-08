def run(inputs, settings):
    return {"G": inputs["a"] * inputs["d"] ** inputs["b"]}


def symbolic():
    import sympy as sp
    a, b, d = sp.symbols("a b d", positive=True)
    return {"G": a * d ** b}
