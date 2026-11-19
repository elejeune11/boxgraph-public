import math


def run(inputs, settings):
    # compressive stresses over sigma_0: -sigma_x/sigma_0 and -sigma_y/sigma_0 of Eqs. 4a, 4b
    e = math.exp(-abs(inputs["x"]) / inputs["l"])
    return {"sx": 1 - e, "sy": 1 - inputs["nu_m"] * e}


def symbolic():
    import sympy as sp
    x = sp.symbols("x", real=True)
    l, nu_m = sp.symbols("l nu_m", positive=True)
    e = sp.exp(-sp.Abs(x) / l)
    return {"sx": 1 - e, "sy": 1 - nu_m * e}
