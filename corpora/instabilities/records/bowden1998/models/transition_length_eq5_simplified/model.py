def run(inputs, settings):
    l_over_t = 0.3 * inputs["Em"] / inputs["Ep"]
    return {"l": l_over_t * inputs["t"] / 1000.0, "l_over_t": l_over_t}


def symbolic():
    import sympy as sp
    Em, Ep, t = sp.symbols("Em Ep t", positive=True)
    l_over_t = sp.Rational(3, 10) * Em / Ep
    return {"l": l_over_t * t / 1000, "l_over_t": l_over_t}
