# The accelerating waves are 2, 5 and 6 (Table 1 and the shading of Figs. 3 and 5); 1, 3 and 4 decelerate.


def run(inputs, settings):
    a = inputs["p2"] + inputs["p5"]
    return {"s": 100.0 * a / (a + inputs["p6"])}


def symbolic():
    import sympy as sp
    p2, p5, p6 = sp.symbols("p2 p5 p6", positive=True)
    return {"s": 100 * (p2 + p5) / (p2 + p5 + p6)}
