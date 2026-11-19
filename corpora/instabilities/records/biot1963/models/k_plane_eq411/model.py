def run(inputs, settings):
    return {"k": inputs["lam"] ** 2}


def symbolic():
    import sympy as sp
    lam = sp.symbols("lam", positive=True)
    return {"k": lam**2}
