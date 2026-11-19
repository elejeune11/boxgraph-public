def run(inputs, settings):
    return {"r_w": 1.0 / inputs["g_w"], "r_l": 1.0 / inputs["g_l"]}


def symbolic():
    import sympy as sp
    g_w, g_l = sp.symbols("g_w g_l", positive=True)
    return {"r_w": 1 / g_w, "r_l": 1 / g_l}
