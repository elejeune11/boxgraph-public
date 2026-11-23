def run(inputs, settings):
    kT = inputs["kB"] * inputs["T"] / 1e-21  # pN nm, as talin_WT_model.m line 75
    return {"xt": kT / inputs["Fd"]}


def symbolic():
    import sympy as sp
    kB, T, Fd = sp.symbols("kB T Fd")
    return {"xt": kB * T / sp.Float(1e-21) / Fd}
