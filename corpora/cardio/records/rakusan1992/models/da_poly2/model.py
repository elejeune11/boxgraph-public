# Second-order polynomial in heart mass, coefficients as printed.


def run(inputs, settings):
    x = inputs["x"]
    return {"y": inputs["b0"] + inputs["b1"] * x + inputs["b2"] * x**2}


def symbolic():
    import sympy as sp
    b0, b1, b2, x = sp.symbols("b0 b1 b2 x", real=True)
    return {"y": b0 + b1 * x + b2 * x**2}
