def run(inputs, settings):
    return {"SWI": inputs["SW"] / inputs["B"]}


def symbolic():
    import sympy as sp
    SW, B = sp.symbols("SW B", positive=True)
    return {"SWI": SW / B}
