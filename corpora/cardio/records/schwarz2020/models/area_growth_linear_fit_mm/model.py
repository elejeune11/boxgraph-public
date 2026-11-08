def run(inputs, settings):
    return {"A": inputs["c_d"] * inputs["dM"] + inputs["c_S"] * inputs["S"] + inputs["c_0"]}


def symbolic():
    import sympy as sp
    c_d, c_S, c_0, dM, S = sp.symbols("c_d c_S c_0 dM S")
    return {"A": c_d * dM + c_S * S + c_0}
