def run(inputs, settings):
    return {"E_ex": inputs["E_rest"] * (1.0 + inputs["r"] / 100.0)}


def symbolic():
    import sympy as sp
    E_rest, r = sp.symbols("E_rest r", positive=True)
    return {"E_ex": E_rest * (1 + r / 100)}
