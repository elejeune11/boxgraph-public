# Eq. 3 divided by ro: lambda/ro equals the scaled expression plotted on the abscissa of Fig. 4b.


def run(inputs, settings):
    return {"y": inputs["X"]}


def symbolic():
    import sympy as sp
    X = sp.symbols("X", positive=True)
    return {"y": X}
