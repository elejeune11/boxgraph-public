# F = k u: nN/um * um = nN.


def run(inputs, settings):
    return {"F": inputs["k"] * inputs["u"]}


def symbolic():
    import sympy as sp
    k, u = sp.symbols("k u", positive=True)
    return {"F": k * u}
