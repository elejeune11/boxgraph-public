# Ratio of the optimal nc on the stiff substrate to that on the soft one ("increased by a factor of").


def run(inputs, settings):
    return {"ratio": inputs["n_stiff"] / inputs["n_soft"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("n_stiff n_soft", positive=True)
    return {"ratio": a / b}
