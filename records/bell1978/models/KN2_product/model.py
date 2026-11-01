def run(inputs, settings):
    return {"KN2": inputs["Km"] * inputs["N2"]}


def symbolic():
    import sympy as sp
    Km, N2 = sp.symbols("Km N2", positive=True)
    return {"KN2": Km * N2}
