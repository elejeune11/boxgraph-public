def run(inputs, settings):
    return {"Zdc": inputs["Rc"] + inputs["Rp"]}


def symbolic():
    import sympy as sp
    Rc, Rp = sp.symbols("Rc Rp", positive=True)
    return {"Zdc": Rc + Rp}
