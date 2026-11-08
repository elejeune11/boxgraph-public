def run(inputs, settings):
    return {"Rc": inputs["Ra"] + inputs["Rv"]}


def symbolic():
    import sympy as sp
    Ra, Rv = sp.symbols("Ra Rv", positive=True)
    return {"Rc": Ra + Rv}
