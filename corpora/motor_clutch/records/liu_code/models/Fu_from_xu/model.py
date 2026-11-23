def run(inputs, settings):
    kT = inputs["kB"] * inputs["T"] / 1e-21  # pN nm, talin_WT_model.m line 75
    return {"Fu": kT / inputs["x_u"]}  # line 79


def symbolic():
    import sympy as sp
    kB, T, x_u = sp.symbols("kB T x_u")
    return {"Fu": kB * T / sp.Float(1e-21) / x_u}
