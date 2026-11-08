def run(inputs, settings):
    return {"ratio": 10 ** inputs["b"]}


def symbolic():
    import sympy as sp
    b = sp.symbols("b", real=True)
    return {"ratio": 10 ** b}
