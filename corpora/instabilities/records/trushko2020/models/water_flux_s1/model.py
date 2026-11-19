def run(inputs, settings):
    return {"J": inputs["V"] / 2.0 / (inputs["A"] * inputs["T"])}


def symbolic():
    import sympy as sp
    V, A, T = sp.symbols("V A T", positive=True)
    return {"J": V / 2 / (A * T)}
