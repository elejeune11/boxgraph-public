def run(inputs, settings):
    return {"r": inputs["koff2"] / inputs["koff1"]}


def symbolic():
    import sympy as sp
    koff1, koff2 = sp.symbols("koff1 koff2", positive=True)
    return {"r": koff2 / koff1}
