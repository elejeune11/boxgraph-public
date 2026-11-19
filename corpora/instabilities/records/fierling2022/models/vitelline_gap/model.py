def run(inputs, settings):
    return {"d": inputs["c"] * inputs["R_DV"]}


def symbolic():
    import sympy as sp
    c, R = sp.symbols("c R_DV", positive=True)
    return {"d": c * R}
