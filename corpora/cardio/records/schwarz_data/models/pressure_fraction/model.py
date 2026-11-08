# Our own arithmetic: a pressure as a percentage of the inlet pressure.
def run(inputs, settings):
    return {"f": 100.0 * inputs["P"] / inputs["P_in"]}


def symbolic():
    import sympy as sp
    P, P_in = sp.symbols("P P_in", positive=True)
    return {"f": 100 * P / P_in}
