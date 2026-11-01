from math import comb


def lifetime(n0, g):
    """Eq. 8, dimensionless."""
    s = sum(comb(n0, n) * g**n / n for n in range(1, n0 + 1))
    h = sum(1.0 / i for i in range(1, n0 + 1))
    return (s + h) / (1 + g)


def run(inputs, settings):
    return {"T": lifetime(int(round(inputs["N0"])), inputs["gamma"]) / inputs["k0"]}
