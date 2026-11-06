def run(inputs, settings):
    return {"tau": inputs["Rp"] * inputs["C"]}


def symbolic():
    import sympy as sp
    Rp, C = sp.symbols("Rp C", positive=True)
    return {"tau": Rp * C}
