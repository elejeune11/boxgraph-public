from math import comb


def lifetime(n0, g):
    """Eq. 8, dimensionless (same as lifetime_eq8)."""
    s = sum(comb(n0, n) * g**n / n for n in range(1, n0 + 1))
    h = sum(1.0 / i for i in range(1, n0 + 1))
    return (s + h) / (1 + g)


def run(inputs, settings):
    target, g = inputs["T"] * inputs["k0"], inputs["gamma"]
    for n0 in range(1, settings["n_max"] + 1):
        if lifetime(n0, g) >= target:
            return {"N0": float(n0)}
    return {"N0": float("nan")}
