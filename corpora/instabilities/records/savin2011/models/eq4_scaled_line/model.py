# Eq. 4 divided by ro: R/ro equals the scaled expression plotted on the abscissa of Fig. 4c.


def run(inputs, settings):
    return {"y": inputs["X"]}


def symbolic():
    import sympy as sp
    X = sp.symbols("X", positive=True)
    return {"y": X}
