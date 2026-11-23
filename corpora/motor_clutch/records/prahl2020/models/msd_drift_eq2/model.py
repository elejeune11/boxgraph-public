def run(inputs, settings):
    n, mu, v, t = inputs["n"], inputs["mu"], inputs["v"], inputs["t"]
    return {"msd": 2.0 * n * mu * t + v ** 2 * t ** 2}


def symbolic():
    import sympy as sp
    n, mu, v, t = sp.symbols("n mu v t", positive=True)
    return {"msd": 2 * n * mu * t + v ** 2 * t ** 2}
