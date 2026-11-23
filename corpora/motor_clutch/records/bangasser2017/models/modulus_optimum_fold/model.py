def run(inputs, settings):
    return {"fold": inputs["E_a"] / inputs["E_b"]}


def symbolic():
    import sympy as sp
    E_a, E_b = sp.symbols("E_a E_b", positive=True)
    return {"fold": E_a / E_b}
