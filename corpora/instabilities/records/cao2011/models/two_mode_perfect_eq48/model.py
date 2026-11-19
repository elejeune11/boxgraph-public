# Eq. 4.8: the perfect two-mode post-bifurcation path, D = lambda - lambda_W >= 0.


def run(inputs, settings):
    b, D = inputs["b112"], inputs["D"]
    return {"xi1_pos": 2.0 * D / b, "xi1_neg": -2.0 * D / b, "xi2": -D / b}


def symbolic():
    import sympy as sp
    b, D = sp.symbols("b112 D", positive=True)
    return {"xi1_pos": 2 * D / b, "xi1_neg": -2 * D / b, "xi2": -D / b}
