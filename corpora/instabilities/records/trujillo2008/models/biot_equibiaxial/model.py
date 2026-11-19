# Biot's surface-instability condition lambda1^2 lambda3 = const, specialised to equibiaxial
# compression lambda1 = lambda3 = lambda, and the strain e_c = 1 - lambda (p. 2).


def run(inputs, settings):
    lam = inputs["lam_prod"] ** (1.0 / 3.0)
    return {"e_c": 1.0 - lam}


def symbolic():
    import sympy as sp
    lam_prod = sp.symbols("lam_prod", positive=True)
    return {"e_c": 1 - lam_prod ** sp.Rational(1, 3)}
