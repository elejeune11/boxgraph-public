def run(inputs, settings):
    return {"kon": inputs["r"] * inputs["koff"]}


def symbolic():
    import sympy as sp
    r, koff = sp.symbols("r koff", positive=True)
    return {"kon": r * koff}
