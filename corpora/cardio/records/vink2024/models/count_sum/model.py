# Total of two disjoint counts. Dimensionless.


def run(inputs, settings):
    return {"total": inputs["a"] + inputs["b"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("a b", nonnegative=True)
    return {"total": a + b}
