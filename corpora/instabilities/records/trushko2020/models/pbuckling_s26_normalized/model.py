# Eq. S26 divided by K/R^3: P R^3/K = (lambda R^2/K)^(2/5); printed with "proportional to",
# prefactor 1.


def run(inputs, settings):
    return {"p": inputs["Lam"] ** 0.4}


def symbolic():
    import sympy as sp
    Lam = sp.symbols("Lam", positive=True)
    return {"p": Lam ** sp.Rational(2, 5)}
