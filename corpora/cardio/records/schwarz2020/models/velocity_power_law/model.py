def run(inputs, settings):
    return {"v": inputs["a"] * inputs["d"] ** inputs["b"]}


def symbolic():
    import sympy as sp
    a, b, d = sp.symbols("a b d", positive=True)
    return {"v": a * d ** b}
