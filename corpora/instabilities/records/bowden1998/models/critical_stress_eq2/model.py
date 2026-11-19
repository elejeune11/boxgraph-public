def run(inputs, settings):
    Em_bar = inputs["Em"] / (1 - inputs["nu_m"] ** 2)
    Ep_bar = inputs["Ep"] / (1 - inputs["nu_p"] ** 2)
    return {"sigma_crit": 0.52 * Em_bar ** (1 / 3) * Ep_bar ** (2 / 3) / 1e6}


def symbolic():
    import sympy as sp
    Em, Ep, nu_m, nu_p = sp.symbols("Em Ep nu_m nu_p", positive=True)
    Em_bar = Em / (1 - nu_m**2)
    Ep_bar = Ep / (1 - nu_p**2)
    return {"sigma_crit": sp.Rational(52, 100) * Em_bar ** sp.Rational(1, 3) * Ep_bar ** sp.Rational(2, 3) / 10**6}
