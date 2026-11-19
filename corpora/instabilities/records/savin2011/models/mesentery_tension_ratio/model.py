# p. 5: mesentery tension Em h eps0, ratio of embryo 1 to embryo 2 (same units on both sides).


def run(inputs, settings):
    t1 = inputs["Em1"] * inputs["h1"] * inputs["e1"]
    t2 = inputs["Em2"] * inputs["h2"] * inputs["e2"]
    return {"ratio": t1 / t2}


def symbolic():
    import sympy as sp
    Em1, h1, e1, Em2, h2, e2 = sp.symbols("Em1 h1 e1 Em2 h2 e2", positive=True)
    return {"ratio": Em1 * h1 * e1 / (Em2 * h2 * e2)}
