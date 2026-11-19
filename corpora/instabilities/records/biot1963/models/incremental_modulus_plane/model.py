def run(inputs, settings):
    lam = inputs["lam"]
    return {"mu": 0.5 * (lam**2 + 1 / lam**2)}


def symbolic():
    import sympy as sp
    lam = sp.symbols("lam", positive=True)
    return {"mu": (lam**2 + 1 / lam**2) / 2}
