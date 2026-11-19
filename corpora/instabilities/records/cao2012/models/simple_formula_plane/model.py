def run(inputs, settings):
    lam = 0.5 * (1 + inputs["lam01"] ** 2)
    x = lam * 3 / inputs["mu_ratio"]
    return {"e0": 0.25 * x ** (2 / 3), "k0h": x ** (1 / 3)}


def symbolic():
    import sympy as sp
    mu_ratio, lam01 = sp.symbols("mu_ratio lam01", positive=True)
    x = sp.Rational(1, 2) * (1 + lam01**2) * 3 / mu_ratio
    return {"e0": sp.Rational(1, 4) * x ** sp.Rational(2, 3), "k0h": x ** sp.Rational(1, 3)}
