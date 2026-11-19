# G proportional to the cross-linker mole fraction (p. 3); prefactor unknown, written as 1 kPa per mol%.


def run(inputs, settings):
    return {"G": inputs["x"]}


def symbolic():
    import sympy as sp
    x = sp.symbols("x", positive=True)
    return {"G": x}
