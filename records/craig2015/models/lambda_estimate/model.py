def run(inputs, settings):
    drag = inputs["T0"] * inputs["L0"] ** 2 / inputs["V0"]
    mu = inputs["eta"] * inputs["h"]
    return {"drag": drag, "lam": mu / drag}


def symbolic():
    import sympy as sp
    T0, L0, V0, eta, h = sp.symbols("T0 L0 V0 eta h", positive=True)
    drag = T0 * L0 ** 2 / V0
    return {"drag": drag, "lam": eta * h / drag}
