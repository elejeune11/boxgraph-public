def run(inputs, settings):
    ratio = inputs["Em"] * (1 - inputs["nu_p"] ** 2) / (inputs["Ep"] * (1 - inputs["nu_m"] ** 2))
    L_over_t = 4.36 * ratio ** (1 / 3)
    return {"L": L_over_t * inputs["t"] / 1000.0, "L_over_t": L_over_t}


def symbolic():
    import sympy as sp
    Em, Ep, nu_m, nu_p, t = sp.symbols("Em Ep nu_m nu_p t", positive=True)
    L_over_t = sp.Rational(436, 100) * (Em * (1 - nu_p**2) / (Ep * (1 - nu_m**2))) ** sp.Rational(1, 3)
    return {"L": L_over_t * t / 1000, "L_over_t": L_over_t}
