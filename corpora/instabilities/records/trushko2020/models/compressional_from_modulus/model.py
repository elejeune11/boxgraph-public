def run(inputs, settings):
    # kPa * um = 1e-3 N/m
    return {"lam": inputs["E_mono"] * inputs["a"] * 1e-3}


def symbolic():
    import sympy as sp
    E, a = sp.symbols("E_mono a", positive=True)
    return {"lam": E * a * sp.Rational(1, 1000)}
