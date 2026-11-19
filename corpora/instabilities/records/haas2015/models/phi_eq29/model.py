# Eq. 2.9: Phi = r(1) = [(1 - nu) + (1 + nu) f] / 2, lengths in units of the disc radius R.


def run(inputs, settings):
    nu, f = inputs["nu"], inputs["f"]
    return {"Phi": 0.5 * ((1.0 - nu) + (1.0 + nu) * f)}


def symbolic():
    import sympy as sp
    nu, f = sp.symbols("nu f", positive=True)
    return {"Phi": sp.Rational(1, 2) * ((1 - nu) + (1 + nu) * f)}
