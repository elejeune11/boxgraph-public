def run(inputs, settings):
    return {"rate": inputs["k_plus_m"] * inputs["N1"] * inputs["N2"]}


def symbolic():
    import sympy as sp
    k_plus_m, N1, N2 = sp.symbols("k_plus_m N1 N2", positive=True)
    return {"rate": k_plus_m * N1 * N2}
