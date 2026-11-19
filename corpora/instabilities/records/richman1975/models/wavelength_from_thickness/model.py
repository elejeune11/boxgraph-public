def run(inputs, settings):
    return {"l": inputs["l_over_t"] * inputs["t"]}


def symbolic():
    import sympy as sp
    r, t = sp.symbols("l_over_t t", positive=True)
    return {"l": r * t}
