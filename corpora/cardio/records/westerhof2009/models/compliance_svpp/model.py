def run(inputs, settings):
    return {"C": inputs["DV"] / inputs["DP"]}


def symbolic():
    import sympy as sp
    DV, DP = sp.symbols("DV DP", positive=True)
    return {"C": DV / DP}
