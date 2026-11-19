def run(inputs, settings):
    return {"g": 0.75 * inputs["kH"] ** -3}


def symbolic():
    import sympy as sp
    kH = sp.symbols("kH", positive=True)
    return {"g": sp.Rational(3, 4) * kH ** -3}
