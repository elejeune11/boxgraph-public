def run(inputs, settings):
    return {"t": inputs["d"] * 1e-4 / inputs["v"]}  # um -> cm


def symbolic():
    import sympy as sp
    d, v = sp.symbols("d v", positive=True)
    return {"t": d * sp.Rational(1, 10**4) / v}
