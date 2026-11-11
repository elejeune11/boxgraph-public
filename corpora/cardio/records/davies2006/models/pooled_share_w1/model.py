# Weighted mean of two group means (n1 and N - n1 subjects).


def run(inputs, settings):
    N, n1 = inputs["N"], inputs["n1"]
    return {"mean": (n1 * inputs["m1"] + (N - n1) * inputs["m2"]) / N}


def symbolic():
    import sympy as sp
    N, n1, m1, m2 = sp.symbols("N n1 m1 m2", positive=True)
    return {"mean": (n1 * m1 + (N - n1) * m2) / N}
