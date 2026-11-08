def run(inputs, settings):
    return {"ratio": (inputs["d1"] / inputs["d2"]) ** inputs["gamma"]}


def symbolic():
    import sympy as sp
    gamma, d1, d2 = sp.symbols("gamma d1 d2", positive=True)
    return {"ratio": (d1 / d2) ** gamma}
