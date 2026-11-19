# lambda ~ t (E/Es)^(1/3), printed with "~" and no prefactor; evaluated with prefactor 1,
# as the paper does in its estimate lambda ~ 3t for E/Es ~ 10. t and lambda in mm.


def run(inputs, settings):
    r = inputs["E_over_Es"] ** (1.0 / 3.0)
    return {"lam": inputs["t"] * r, "lam_over_t": r}


def symbolic():
    import sympy as sp
    t, E_over_Es = sp.symbols("t E_over_Es", positive=True)
    r = E_over_Es ** sp.Rational(1, 3)
    return {"lam": t * r, "lam_over_t": r}
