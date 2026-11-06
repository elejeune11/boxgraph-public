def run(inputs, settings):
    # the paper's own conversion factor 1.6e-5 dyne per (eV/nm)
    return {"f0": 1.6e-5 * inputs["E0"] / inputs["r0"]}


def symbolic():
    import sympy as sp
    E0, r0 = sp.symbols("E0 r0", positive=True)
    return {"f0": sp.Rational(16, 10**6) * E0 / r0}
