def run(inputs, settings):
    L_over_t = 4.4 * (inputs["Em"] / inputs["Ep"]) ** (1 / 3)
    return {"L": L_over_t * inputs["t"] / 1000.0, "L_over_t": L_over_t}


def symbolic():
    import sympy as sp
    Em, Ep, t = sp.symbols("Em Ep t", positive=True)
    L_over_t = sp.Rational(44, 10) * (Em / Ep) ** sp.Rational(1, 3)
    return {"L": L_over_t * t / 1000, "L_over_t": L_over_t}
