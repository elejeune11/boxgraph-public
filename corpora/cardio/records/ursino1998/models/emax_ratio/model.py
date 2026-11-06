# Ratio of the right to the left end-systolic elastance (p. 4): Emax,rv / Emax,lv.
def run(inputs, settings):
    return {"ratio": inputs["Emax_rv"] / inputs["Emax_lv"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("Emax_rv Emax_lv", positive=True)
    return {"ratio": a / b}
