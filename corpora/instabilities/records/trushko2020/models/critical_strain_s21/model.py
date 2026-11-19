def run(inputs, settings):
    # uN*um / (uN/um * um^2) is dimensionless
    x = 30.0 * (5.0 / 2.0) ** (2.0 / 3.0) * inputs["K"] / (inputs["lam"] * inputs["R"] ** 2)
    return {"delta_c": x ** (3.0 / 5.0)}


def symbolic():
    import sympy as sp
    K, lam, R = sp.symbols("K lam R", positive=True)
    return {"delta_c": (30 * sp.Rational(5, 2) ** sp.Rational(2, 3) * K / (lam * R ** 2)) ** sp.Rational(3, 5)}
