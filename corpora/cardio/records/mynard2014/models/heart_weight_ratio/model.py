def run(inputs, settings):
    hw_a = inputs["r_a"] * inputs["BW_a"]  # g/kg * kg = g
    hw_n = inputs["r_n"] * inputs["BW_n"]
    return {"ratio": hw_a / hw_n}


def symbolic():
    import sympy as sp
    r_a, BW_a, r_n, BW_n = sp.symbols("r_a BW_a r_n BW_n", positive=True)
    return {"ratio": (r_a * BW_a) / (r_n * BW_n)}
