# the paper's "fivefold higher for avb6 than for a5b1" (p. 2), as arithmetic on a density


def run(inputs, settings):
    return {"n2": inputs["d_ratio"] * inputs["n1"]}


def symbolic():
    import sympy as sp
    d_ratio, n1 = sp.symbols("d_ratio n1", positive=True)
    return {"n2": d_ratio * n1}
