def run(inputs, settings):
    return {"phi_sum": inputs["phi_c"] + inputs["phi_a"]}


def symbolic():
    import sympy as sp
    phi_c, phi_a = sp.symbols("phi_c phi_a", positive=True)
    return {"phi_sum": phi_c + phi_a}
