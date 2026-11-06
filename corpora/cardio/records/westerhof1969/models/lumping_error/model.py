def run(inputs, settings):
    x = inputs["gdz"] / 2
    return {"err_L": 100 * x, "err_pi": 100 * x**2}


def symbolic():
    import sympy as sp
    g = sp.symbols("gdz", positive=True)
    return {"err_L": 100 * g / 2, "err_pi": 100 * (g / 2) ** 2}
