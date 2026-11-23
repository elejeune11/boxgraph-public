def run(inputs, settings):
    return {"rate": inputs["v"]}


def symbolic():
    import sympy as sp
    v = sp.symbols("v", positive=True)
    return {"rate": v}
