# Eq. 5 with Lambda = (1 + lambda_p^2)/2 (corrected variant of eq5_stiff_film).


def run(inputs, settings):
    lam = (1 + inputs["lam_p"] ** 2) / 2
    return {"e_wrinkle": 0.25 * (lam * 3 / inputs["mu_ratio"]) ** (2 / 3)}


def symbolic():
    import sympy as sp
    mu_ratio, lam_p = sp.symbols("mu_ratio lam_p", positive=True)
    return {"e_wrinkle": sp.Rational(1, 4) * ((1 + lam_p**2) / 2 * 3 / mu_ratio) ** sp.Rational(2, 3)}
