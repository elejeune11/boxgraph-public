def run(inputs, settings):
    # output per hectogram (100 g): M in g -> hg is / 100
    return {"c": inputs["Cim"] / (inputs["M"] / 100.0)}


def symbolic():
    import sympy as sp
    Cim, M = sp.symbols("Cim M", positive=True)
    return {"c": Cim / (M / 100)}
