# Mass of a layer of the given sectional area and thickness at the given density.


def run(inputs, settings):
    return {"m": inputs["rho"] * inputs["A"] * inputs["h"] * 1e-3}


def symbolic():
    import sympy as sp
    A, h, rho = sp.symbols("A h rho", positive=True)
    return {"m": rho * A * h * sp.Rational(1, 1000)}
