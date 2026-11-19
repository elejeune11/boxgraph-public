# SI p. 8: b1par h = c k1 a1^3; divided by k2 a1^3 this is the line of Fig. S6c, y = c (k1/k2).


def run(inputs, settings):
    return {"y": inputs["c"] * inputs["r"]}


def symbolic():
    import sympy as sp
    c, r = sp.symbols("c r", positive=True)
    return {"y": c * r}
