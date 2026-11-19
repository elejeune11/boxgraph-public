def run(inputs, settings):
    return {"t": inputs["t1"] + inputs["t2"]}


def symbolic():
    import sympy as sp
    t1, t2 = sp.symbols("t1 t2", positive=True)
    return {"t": t1 + t2}
