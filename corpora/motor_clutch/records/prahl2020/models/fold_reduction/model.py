def run(inputs, settings):
    return {"nclutch_reduced": inputs["nclutch"] / inputs["fold"]}


def symbolic():
    import sympy as sp
    nclutch, fold = sp.symbols("nclutch fold", positive=True)
    return {"nclutch_reduced": nclutch / fold}
