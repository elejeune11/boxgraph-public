# Total of three disjoint counts. Dimensionless.


def run(inputs, settings):
    return {"total": inputs["a"] + inputs["b"] + inputs["c"]}


def symbolic():
    import sympy as sp
    a, b, c = sp.symbols("a b c", nonnegative=True)
    return {"total": a + b + c}
