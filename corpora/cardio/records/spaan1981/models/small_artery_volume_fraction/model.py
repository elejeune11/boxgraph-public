def run(inputs, settings):
    return {"phi_a": inputs["phi_c"] / 3.0}


def symbolic():
    import sympy as sp
    phi_c = sp.symbols("phi_c", positive=True)
    return {"phi_a": phi_c / 3}
