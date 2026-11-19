# Fig. 1(c) dashed line, as labelled: g = 1 + (3/(8 eta))^(2/3).


def run(inputs, settings):
    return {"g": 1.0 + (3.0 / (8.0 * inputs["eta"])) ** (2.0 / 3.0)}


def symbolic():
    import sympy as sp
    eta = sp.symbols("eta", positive=True)
    return {"g": 1 + (3 / (8 * eta)) ** sp.Rational(2, 3)}
