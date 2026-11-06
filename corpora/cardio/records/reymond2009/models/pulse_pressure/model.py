def run(inputs, settings):
    return {"PP": inputs["Ps"] - inputs["Pd"]}


def symbolic():
    import sympy as sp
    Ps, Pd = sp.symbols("Ps Pd", positive=True)
    return {"PP": Ps - Pd}
