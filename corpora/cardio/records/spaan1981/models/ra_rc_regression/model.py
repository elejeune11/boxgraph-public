def run(inputs, settings):
    return {"Ra": inputs["b"] * inputs["Rc"] + inputs["a"]}


def symbolic():
    import sympy as sp
    b, a, Rc = sp.symbols("b a Rc", real=True)
    return {"Ra": b * Rc + a}
