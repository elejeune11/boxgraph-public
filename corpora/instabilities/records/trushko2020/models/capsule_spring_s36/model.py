import math


def run(inputs, settings):
    # sqrt(uN/um * uN*um) = uN; divided by um gives uN/um
    return {"k_cap": 4.0 * math.sqrt(inputs["lambda_cap"] * inputs["Kcap"]) / inputs["R"]}


def symbolic():
    import sympy as sp
    lc, Kc, R = sp.symbols("lambda_cap Kcap R", positive=True)
    return {"k_cap": 4 * sp.sqrt(lc * Kc) / R}
