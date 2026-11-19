def run(inputs, settings):
    lam = inputs["lam"]
    return {"P": 1 / lam - lam**2}


def symbolic():
    import sympy as sp
    lam = sp.symbols("lam", positive=True)
    return {"P": 1 / lam - lam**2}
