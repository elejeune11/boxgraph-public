def run(inputs, settings):
    return {"r": inputs["kont2"] / inputs["kont1"]}


def symbolic():
    import sympy as sp
    kont1, kont2 = sp.symbols("kont1 kont2", positive=True)
    return {"r": kont2 / kont1}
