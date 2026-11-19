def run(inputs, settings):
    l0 = inputs["lam01"]
    lam = 0.5 * l0 ** 0.5 * (1 + l0 ** 1.5)
    x = lam * 3 / inputs["mu_ratio"]
    return {"e0": x ** (2 / 3) / 3, "k0h": x ** (1 / 3)}


def symbolic():
    import sympy as sp
    mu_ratio, lam01 = sp.symbols("mu_ratio lam01", positive=True)
    x = sp.Rational(1, 2) * sp.sqrt(lam01) * (1 + lam01 ** sp.Rational(3, 2)) * 3 / mu_ratio
    return {"e0": x ** sp.Rational(2, 3) / 3, "k0h": x ** sp.Rational(1, 3)}
