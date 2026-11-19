# SI p. 8: b1par h = c k1 a1^3 and b1par h = 2 b1 a1 give k1 a1^2 = (2/c) b1.


def run(inputs, settings):
    return {"ratio": 2.0 / inputs["c"]}


def symbolic():
    import sympy as sp
    c = sp.symbols("c", positive=True)
    return {"ratio": 2 / c}
