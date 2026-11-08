def run(inputs, settings):
    rc = inputs["Rc"]
    return {"f": (inputs["b"] * rc + inputs["a"]) / rc}


def symbolic():
    import sympy as sp
    b, a, Rc = sp.symbols("b a Rc", real=True)
    return {"f": (b * Rc + a) / Rc}
