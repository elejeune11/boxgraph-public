import math


def run(inputs, settings):
    d = inputs["d"]
    hd = inputs["Hd"]
    mu045 = 6 * math.exp(-0.085 * d) + 3.2 - 2.44 * math.exp(-0.06 * d ** 0.645)
    s = 1 / (1 + 1e-11 * d ** 12)
    c = (0.8 + math.exp(-0.075 * d)) * (-1 + s) + s
    r = (d / (d - 1.1)) ** 2
    mu = (1 + (mu045 - 1) * ((1 - hd) ** c - 1) / ((1 - 0.45) ** c - 1) * r) * r
    return {"mu": mu}


def symbolic():
    import sympy as sp
    d, Hd = sp.symbols("d Hd", positive=True)
    mu045 = 6 * sp.exp(-sp.Rational(85, 1000) * d) + sp.Rational(32, 10) - sp.Rational(244, 100) * sp.exp(-sp.Rational(6, 100) * d ** sp.Rational(645, 1000))
    s = 1 / (1 + sp.Rational(1, 10 ** 11) * d ** 12)
    c = (sp.Rational(8, 10) + sp.exp(-sp.Rational(75, 1000) * d)) * (-1 + s) + s
    r = (d / (d - sp.Rational(11, 10))) ** 2
    return {"mu": (1 + (mu045 - 1) * ((1 - Hd) ** c - 1) / ((1 - sp.Rational(45, 100)) ** c - 1) * r) * r}
