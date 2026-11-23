def run(inputs, settings):
    return {"nclutch_module": inputs["f"] * inputs["nclutch"]}


def symbolic():
    import sympy as sp
    f, nclutch = sp.symbols("f nclutch", positive=True)
    return {"nclutch_module": f * nclutch}
