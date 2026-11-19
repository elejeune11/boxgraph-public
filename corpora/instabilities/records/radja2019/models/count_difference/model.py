def run(inputs, settings):
    return {"n_rest": inputs["n_all"] - inputs["n_part"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("n_all n_part")
    return {"n_rest": a - b}
