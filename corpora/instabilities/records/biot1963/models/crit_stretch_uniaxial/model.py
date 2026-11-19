def run(inputs, settings):
    # (1 - lam^3)/(1 + lam^3) = zeta  ->  lam^3 = (1 - zeta)/(1 + zeta), the positive real root
    z = inputs["zeta"]
    return {"lam": ((1 - z) / (1 + z)) ** (1.0 / 3.0)}


def symbolic():
    import sympy as sp
    zeta = sp.symbols("zeta", positive=True)
    return {"lam": ((1 - zeta) / (1 + zeta)) ** sp.Rational(1, 3)}
