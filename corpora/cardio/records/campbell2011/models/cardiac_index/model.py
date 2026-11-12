def run(inputs, settings):
    return {"CI": inputs["CO"] / inputs["B"]}


def symbolic():
    import sympy as sp
    CO, B = sp.symbols("CO B", positive=True)
    return {"CI": CO / B}
