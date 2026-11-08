def run(inputs, settings):
    s, g = inputs["S"], inputs["gamma"]
    return {"A": (1 + s ** 2) / (1 + s ** g) ** (2 / g)}


def symbolic():
    import sympy as sp
    S, gamma = sp.symbols("S gamma", positive=True)
    return {"A": (1 + S ** 2) / (1 + S ** gamma) ** (2 / gamma)}
