def run(inputs, settings):
    return {"k": inputs["lam"] ** 1.5}


def symbolic():
    import sympy as sp
    lam = sp.symbols("lam", positive=True)
    return {"k": lam ** sp.Rational(3, 2)}
