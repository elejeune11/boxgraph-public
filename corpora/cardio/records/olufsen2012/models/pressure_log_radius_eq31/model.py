def run(inputs, settings):
    return {"p": inputs["a"] * inputs["log10r"] + inputs["b"]}


def symbolic():
    import sympy as sp
    a, b, x = sp.symbols("a b log10r", real=True)
    return {"p": a * x + b}
