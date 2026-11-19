def run(inputs, settings):
    # kPa * um = 1e3 * 1e-6 N/m = 1e-3 N/m; 1 uN/um = 1 N/m
    E, h, nu = inputs["E"], inputs["h"], inputs["nu"]
    return {"lambda_cap": E * h / (1.0 - nu ** 2) * 1e-3}


def symbolic():
    import sympy as sp
    E, h, nu = sp.symbols("E h nu", positive=True)
    return {"lambda_cap": E * h / (1 - nu ** 2) * sp.Rational(1, 1000)}
