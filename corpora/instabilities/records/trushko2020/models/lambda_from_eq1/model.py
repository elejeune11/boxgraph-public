def run(inputs, settings):
    # SI units; Equation 1 with prefactor 1, solved for lambda
    return {"lam": (inputs["P"] * inputs["R"] ** 2.2 / inputs["K"] ** 0.6) ** 2.5}


def symbolic():
    import sympy as sp
    P, K, R = sp.symbols("P K R", positive=True)
    return {"lam": (P * R ** sp.Rational(11, 5) / K ** sp.Rational(3, 5)) ** sp.Rational(5, 2)}
