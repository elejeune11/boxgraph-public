def run(inputs, settings):
    return {"phi_k": inputs["k"] * inputs["phi"]}


def symbolic():
    import sympy as sp
    k, phi = sp.symbols("k phi", positive=True)
    return {"phi_k": k * phi}
