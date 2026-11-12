def run(inputs, settings):
    return {"y": inputs["x"]}


def symbolic():
    import sympy as sp
    x = sp.symbols("x", positive=True)
    return {"y": x}
