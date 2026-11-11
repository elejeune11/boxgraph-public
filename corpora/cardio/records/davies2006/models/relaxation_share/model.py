# Waves 4, 5 and 6 are the three "associated with ventricular relaxation" (p. 5).


def run(inputs, settings):
    return {"s": inputs["p4"] + inputs["p5"] + inputs["p6"]}


def symbolic():
    import sympy as sp
    p4, p5, p6 = sp.symbols("p4 p5 p6", positive=True)
    return {"s": p4 + p5 + p6}
