# "left atrial mu_AV was estimated as 2/3 of the right atrial value" (p. 7).


def run(inputs, settings):
    return {"mu_la": 2.0 / 3.0 * inputs["mu_ra"]}


def symbolic():
    import sympy as sp
    mu_ra = sp.Symbol("mu_ra", positive=True)
    return {"mu_la": sp.Rational(2, 3) * mu_ra}
