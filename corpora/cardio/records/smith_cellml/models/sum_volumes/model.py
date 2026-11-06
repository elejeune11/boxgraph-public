# Total of the six initial chamber volumes of the closed loop.

NAMES = ("V_lv", "V_rv", "V_pa", "V_pu", "V_ao", "V_vc")


def run(inputs, settings):
    return {"V_total": sum(inputs[k] for k in NAMES)}


def symbolic():
    import sympy as sp
    s = sp.symbols(" ".join(NAMES), positive=True)
    return {"V_total": sum(s)}
