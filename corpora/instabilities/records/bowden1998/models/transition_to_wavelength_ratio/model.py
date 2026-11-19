def run(inputs, settings):
    X = inputs["Em"] * (1 - inputs["nu_p"] ** 2) / (inputs["Ep"] * (1 - inputs["nu_m"] ** 2))
    return {"l_over_L": (0.3 * X) / (4.36 * X ** (1 / 3))}


def symbolic():
    import sympy as sp
    Em, Ep, nu_m, nu_p = sp.symbols("Em Ep nu_m nu_p", positive=True)
    X = Em * (1 - nu_p**2) / (Ep * (1 - nu_m**2))
    return {"l_over_L": (sp.Rational(3, 10) * X) / (sp.Rational(436, 100) * X ** sp.Rational(1, 3))}
