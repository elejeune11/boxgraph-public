def run(inputs, settings):
    X = inputs["Em"] / inputs["Ep"]
    return {"l_over_L": (0.3 * X) / (4.4 * X ** (1 / 3))}


def symbolic():
    import sympy as sp
    Em, Ep = sp.symbols("Em Ep", positive=True)
    X = Em / Ep
    return {"l_over_L": (sp.Rational(3, 10) * X) / (sp.Rational(44, 10) * X ** sp.Rational(1, 3))}
