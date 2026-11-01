def run(inputs, settings):
    return {"n": inputs["N"] * inputs["A"]}


def symbolic():
    import sympy as sp
    N, A = sp.symbols("N A", positive=True)
    return {"n": N * A}
