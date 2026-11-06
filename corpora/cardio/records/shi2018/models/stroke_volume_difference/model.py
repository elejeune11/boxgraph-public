def run(inputs, settings):
    return {"SV": inputs["V_max"] - inputs["V_min"]}


def symbolic():
    import sympy as sp
    V_max, V_min = sp.symbols("V_max V_min", positive=True)
    return {"SV": V_max - V_min}
