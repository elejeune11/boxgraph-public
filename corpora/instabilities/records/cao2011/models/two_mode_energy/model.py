# b112 xi1^2 xi2 on the path (4.8), per (lambda - lambda_W)^3: b112 (2/b112)^2 (-1/b112) = -4/b112^2.
def run(inputs, settings):
    b = inputs["b112"]
    return {"E": b * (2.0 / b) ** 2 * (-1.0 / b)}


def symbolic():
    import sympy as sp
    b112 = sp.symbols("b112", positive=True)
    return {"E": -4 / b112 ** 2}
