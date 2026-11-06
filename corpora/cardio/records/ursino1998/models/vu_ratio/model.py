# Ratio of the right to the left ventricle unstressed volume (p. 4): Vu,rv / Vu,lv.
def run(inputs, settings):
    return {"ratio": inputs["Vu_rv"] / inputs["Vu_lv"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("Vu_rv Vu_lv", positive=True)
    return {"ratio": a / b}
