# One grid point per square of an orthogonal grid of spacing s: area s^2 (um^2 -> mm^2 is 1e-6).
def run(inputs, settings):
    s, L = inputs["s"], inputs["L"]
    return {"a": s * s * 1e-6, "n": (L / s) ** 2}


def symbolic():
    import sympy as sp
    s, L = sp.symbols("s L", positive=True)
    return {"a": s**2 * sp.Rational(1, 10**6), "n": (L / s) ** 2}
