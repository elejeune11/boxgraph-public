def run(inputs, settings):
    return {"lnl": inputs["a"] * inputs["lnr"] + inputs["b"]}


def symbolic():
    import sympy as sp
    a, b, lnr = sp.symbols("a b lnr", real=True)
    return {"lnl": a * lnr + b}
