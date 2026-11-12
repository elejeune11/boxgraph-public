# Third-order polynomial in heart mass, coefficients as printed.


def run(inputs, settings):
    x = inputs["x"]
    return {"y": inputs["a0"] + inputs["a1"] * x + inputs["a2"] * x**2 + inputs["a3"] * x**3}


def symbolic():
    import sympy as sp
    a0, a1, a2, a3, x = sp.symbols("a0 a1 a2 a3 x", real=True)
    return {"y": a0 + a1 * x + a2 * x**2 + a3 * x**3}
