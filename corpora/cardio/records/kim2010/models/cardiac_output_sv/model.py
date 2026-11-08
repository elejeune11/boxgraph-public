def run(inputs, settings):
    # cc/s -> L/min: x 60 / 1000
    return {"CO": inputs["SV"] / inputs["T"] * 60.0 / 1000.0}


def symbolic():
    import sympy as sp
    SV, T = sp.symbols("SV T", positive=True)
    return {"CO": SV / T * sp.Rational(60, 1000)}
