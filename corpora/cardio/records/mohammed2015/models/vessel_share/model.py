def run(inputs, settings):
    return {"s": 100.0 * inputs["mvd"] / inputs["total"]}


def symbolic():
    import sympy as sp
    mvd, total = sp.symbols("mvd total", positive=True)
    return {"s": 100 * mvd / total}
