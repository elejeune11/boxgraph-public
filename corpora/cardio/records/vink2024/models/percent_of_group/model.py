# A count as a percentage of its denominator. Units: counts dimensionless, output in percent.


def run(inputs, settings):
    return {"pct": 100.0 * inputs["k"] / inputs["n"]}


def symbolic():
    import sympy as sp
    k, n = sp.symbols("k n", positive=True)
    return {"pct": 100 * k / n}
