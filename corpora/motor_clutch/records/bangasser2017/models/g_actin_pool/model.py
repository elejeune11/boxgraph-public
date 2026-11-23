# Actin conservation (words, Methods): the actin not in modules is G-actin. With n modules of
# length lin, AG = Atot - n lin. Units: um.


def run(inputs, settings):
    return {"AG": inputs["Atot"] - inputs["n"] * inputs["lin"]}


def symbolic():
    import sympy as sp
    Atot, n, lin = sp.symbols("Atot n lin", positive=True)
    return {"AG": Atot - n * lin}
