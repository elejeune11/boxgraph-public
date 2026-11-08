def run(inputs, settings):
    # the full swing equals the area; the variation around the mean is half of it
    return {"dV": inputs["A"] / 2.0}


def symbolic():
    import sympy as sp
    A = sp.symbols("A", positive=True)
    return {"dV": A / 2}
