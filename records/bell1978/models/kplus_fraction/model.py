def run(inputs, settings):
    return {"k_plus_m": inputs["fraction"] * inputs["d_plus_m"]}


def symbolic():
    import sympy as sp
    d_plus_m, fraction = sp.symbols("d_plus_m fraction", positive=True)
    return {"k_plus_m": fraction * d_plus_m}
