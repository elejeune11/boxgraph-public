def run(inputs, settings):
    A0 = inputs["A0"] * 1e-12          # um^2 -> m^2
    return {"F_NS": inputs["Fbar"] * inputs["Karea"] * A0 ** 1.5}


def symbolic():
    import sympy as sp
    F, K, A0 = sp.symbols("Fbar Karea A0", positive=True)
    return {"F_NS": F * K * (A0 * sp.Rational(1, 10 ** 12)) ** sp.Rational(3, 2)}
