# Missing share of a measurement, read two ways: over all participants and over the values obtained.
# Counts dimensionless, outputs in percent.


def run(inputs, settings):
    N, n = inputs["N"], inputs["n"]
    return {"of_total": 100.0 * (N - n) / N, "of_obtained": 100.0 * (N - n) / n}


def symbolic():
    import sympy as sp
    N, n = sp.symbols("N n", positive=True)
    return {"of_total": 100 * (N - n) / N, "of_obtained": 100 * (N - n) / n}
