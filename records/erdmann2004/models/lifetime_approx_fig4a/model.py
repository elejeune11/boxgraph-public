import math


def run(inputs, settings):
    # 0.61 is the factor printed in the caption; it is a constant of the stated formula.
    return {"T": math.log(0.61 / inputs["f_over_N0"])}


def symbolic():
    import sympy as sp
    x = sp.symbols("f_over_N0", positive=True)
    return {"T": sp.log(sp.Rational(61, 100) / x)}
