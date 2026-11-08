def run(inputs, settings):
    return {"Q": inputs["a"] * inputs["d"] ** inputs["gamma"]}


def symbolic():
    import sympy as sp
    a, gamma, d = sp.symbols("a gamma d", positive=True)
    return {"Q": a * d ** gamma}
