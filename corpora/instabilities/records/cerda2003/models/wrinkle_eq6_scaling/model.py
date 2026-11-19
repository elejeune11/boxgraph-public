# Eq. 6, a scaling law printed with "~" and no prefactor: lambda ~ (B/K)^(1/4), A ~ (Delta/W)^(1/2) lambda.
# Evaluated with prefactor 1; only its exponents are meaningful (tested as scales_as). SI units.


def run(inputs, settings):
    lam = (inputs["B"] / inputs["K"]) ** 0.25
    return {"lam": lam, "A": (inputs["Delta"] / inputs["W"]) ** 0.5 * lam}


def symbolic():
    import sympy as sp
    B, K, Delta, W = sp.symbols("B K Delta W", positive=True)
    lam = (B / K) ** sp.Rational(1, 4)
    return {"lam": lam, "A": sp.sqrt(Delta / W) * lam}
