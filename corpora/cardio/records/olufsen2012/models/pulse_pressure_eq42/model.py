def run(inputs, settings):
    return {"pulse": inputs["a"] * inputs["pbar"] + inputs["b"]}


def symbolic():
    import sympy as sp
    pbar, a, b = sp.symbols("pbar a b", real=True)
    return {"pulse": a * pbar + b}
