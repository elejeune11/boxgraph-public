def run(inputs, settings):
    x = 10.0 * inputs["K"] / (inputs["lam"] * inputs["R"] ** 2)
    return {"delta_c": x ** (3.0 / 5.0)}


def symbolic():
    import sympy as sp
    K, lam, R = sp.symbols("K lam R", positive=True)
    return {"delta_c": (10 * K / (lam * R ** 2)) ** sp.Rational(3, 5)}
