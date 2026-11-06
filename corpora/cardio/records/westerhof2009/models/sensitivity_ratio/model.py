def run(inputs, settings):
    return {"factor": abs(inputs["S_R"]) / abs(inputs["S_C"])}


def symbolic():
    import sympy as sp
    S_R, S_C = sp.symbols("S_R S_C", positive=True)
    return {"factor": S_R / S_C}
