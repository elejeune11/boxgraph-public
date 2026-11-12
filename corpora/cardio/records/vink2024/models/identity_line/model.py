# The line of perfect agreement: observer-1 MBV equals observer-2 MBV (both mL/mL).


def run(inputs, settings):
    return {"y": inputs["x"]}


def symbolic():
    import sympy as sp
    x = sp.symbols("x", positive=True)
    return {"y": x}
