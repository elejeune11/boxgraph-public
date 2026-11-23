def run(inputs, settings):
    return {"ratio": inputs["A"] / inputs["A_ref"]}


def symbolic():
    import sympy as sp
    A, A_ref = sp.symbols("A A_ref", positive=True)
    return {"ratio": A / A_ref}
