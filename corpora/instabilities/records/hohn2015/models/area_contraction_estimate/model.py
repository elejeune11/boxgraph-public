def run(inputs, settings):
    rp = inputs["rp"]
    return {"dA": 100.0 * (1.0 - rp * rp) / 2.0}


def symbolic():
    import sympy as sp
    rp = sp.symbols("rp", positive=True)
    return {"dA": 100 * (1 - rp**2) / 2}
