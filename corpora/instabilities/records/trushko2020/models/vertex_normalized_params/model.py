def run(inputs, settings):
    ks = inputs["ks"]                    # uN/um = N/m
    cb = inputs["cb"] * 1e-12            # uN*um -> N m
    K = inputs["Karea"]                  # N/m^3
    A0 = inputs["A0"] * 1e-12            # um^2 -> m^2
    ksb = ks / (K * A0)
    cbb = cb / (K * A0 ** 2)
    return {"ks_bar": ksb, "cb_bar": cbb, "ratio": ksb / cbb}


def symbolic():
    import sympy as sp
    ks, cb, K, A0 = sp.symbols("ks cb Karea A0", positive=True)
    a = A0 * sp.Rational(1, 10 ** 12)
    ksb = ks / (K * a)
    cbb = cb * sp.Rational(1, 10 ** 12) / (K * a ** 2)
    return {"ks_bar": ksb, "cb_bar": cbb, "ratio": ksb / cbb}
