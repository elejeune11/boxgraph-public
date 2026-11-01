def run(inputs, settings):
    return {"rate_per_N1": inputs["k_plus_m"] * inputs["N2"]}


def symbolic():
    import sympy as sp
    k_plus_m, N2 = sp.symbols("k_plus_m N2", positive=True)
    return {"rate_per_N1": k_plus_m * N2}
