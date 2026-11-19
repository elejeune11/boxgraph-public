# Incompressible neo-Hookean solid in uniaxial tension: nominal stress S = mu (lambda - lambda^-2).
# mu in kPa, S in Pa.


def run(inputs, settings):
    lam = inputs["lam"]
    return {"S": 1000.0 * inputs["mu"] * (lam - lam ** -2)}


def symbolic():
    import sympy as sp
    mu, lam = sp.symbols("mu lam", positive=True)
    return {"S": 1000 * mu * (lam - lam ** -2)}
