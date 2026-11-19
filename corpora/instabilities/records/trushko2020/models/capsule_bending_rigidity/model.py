def run(inputs, settings):
    # kPa * um^3 = 1e3 N/m^2 * 1e-18 m^3 = 1e-15 N m; 1 uN*um = 1e-12 N m
    E, h, nu = inputs["E"], inputs["h"], inputs["nu"]
    return {"Kcap": E * h ** 3 / (12.0 * (1.0 - nu ** 2)) * 1e-3}


def symbolic():
    import sympy as sp
    E, h, nu = sp.symbols("E h nu", positive=True)
    return {"Kcap": E * h ** 3 / (12 * (1 - nu ** 2)) * sp.Rational(1, 1000)}
