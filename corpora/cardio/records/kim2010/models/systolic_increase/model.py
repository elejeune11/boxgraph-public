def run(inputs, settings):
    return {"P_ex": inputs["P_rest"] * (1.0 + inputs["r"] / 100.0)}


def symbolic():
    import sympy as sp
    P_rest, r = sp.symbols("P_rest r", positive=True)
    return {"P_ex": P_rest * (1 + r / 100)}
