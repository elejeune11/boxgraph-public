def run(inputs, settings):
    return {"f": 100.0 * inputs["P"] / inputs["P_sys"]}


def symbolic():
    import sympy as sp
    P, P_sys = sp.symbols("P P_sys", positive=True)
    return {"f": 100 * P / P_sys}
