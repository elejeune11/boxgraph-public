def run(inputs, settings):
    # (1 - lam^4)/(1 + lam^4) = zeta  ->  lam^4 = (1 - zeta)/(1 + zeta), the positive real root
    z = inputs["zeta"]
    return {"lam": ((1 - z) / (1 + z)) ** 0.25}


def symbolic():
    import sympy as sp
    zeta = sp.symbols("zeta", positive=True)
    return {"lam": ((1 - zeta) / (1 + zeta)) ** sp.Rational(1, 4)}
