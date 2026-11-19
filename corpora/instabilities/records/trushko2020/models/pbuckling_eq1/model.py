def run(inputs, settings):
    # SI units throughout; printed as a scaling, prefactor 1
    return {"P": inputs["lam"] ** 0.4 * inputs["K"] ** 0.6 / inputs["R"] ** 2.2}


def symbolic():
    import sympy as sp
    lam, K, R = sp.symbols("lam K R", positive=True)
    return {"P": lam ** sp.Rational(2, 5) * K ** sp.Rational(3, 5) / R ** sp.Rational(11, 5)}
