def run(inputs, settings):
    # L/min -> cc/s: x 1000 / 60; percent -> fraction: / 100
    return {"Q": inputs["f"] / 100.0 * inputs["CO"] * 1000.0 / 60.0}


def symbolic():
    import sympy as sp
    f, CO = sp.symbols("f CO", positive=True)
    return {"Q": f / 100 * CO * sp.Rational(1000, 60)}
