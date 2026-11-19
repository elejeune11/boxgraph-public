def run(inputs, settings):
    return {"Karea": inputs["lam"] / (inputs["A0"] * 1e-12)}


def symbolic():
    import sympy as sp
    lam, A0 = sp.symbols("lam A0", positive=True)
    return {"Karea": lam / (A0 * sp.Rational(1, 10 ** 12))}
