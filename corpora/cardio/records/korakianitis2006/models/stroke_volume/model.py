def run(inputs, settings):
    return {"SV": inputs["Vmax"] - inputs["Vmin"]}


def symbolic():
    import sympy as sp
    Vmax, Vmin = sp.symbols("Vmax Vmin", positive=True)
    return {"SV": Vmax - Vmin}
