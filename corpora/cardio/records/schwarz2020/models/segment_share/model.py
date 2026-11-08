def run(inputs, settings):
    return {"share": 100.0 * inputs["n"] / inputs["total"]}


def symbolic():
    import sympy as sp
    n, total = sp.symbols("n total", positive=True)
    return {"share": 100 * n / total}
