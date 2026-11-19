def run(inputs, settings):
    ratio = inputs["Em"] * (1 - inputs["nu_p"] ** 2) / (inputs["Ep"] * (1 - inputs["nu_m"] ** 2))
    l_over_t = 0.3 * ratio
    return {"l": l_over_t * inputs["t"] / 1000.0, "l_over_t": l_over_t}


def symbolic():
    import sympy as sp
    Em, Ep, nu_m, nu_p, t = sp.symbols("Em Ep nu_m nu_p t", positive=True)
    l_over_t = sp.Rational(3, 10) * Em * (1 - nu_p**2) / (Ep * (1 - nu_m**2))
    return {"l": l_over_t * t / 1000, "l_over_t": l_over_t}
