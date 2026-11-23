def run(inputs, settings):
    return {"Fdrag": -inputs["dg"] * inputs["A"] * inputs["vcell"]}


def symbolic():
    import sympy as sp
    dg, A, vcell = sp.symbols("dg A vcell", positive=True)
    return {"Fdrag": -dg * A * vcell}
