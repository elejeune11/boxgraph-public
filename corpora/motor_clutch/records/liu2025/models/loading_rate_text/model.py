"""Force-loading rate from talin's extension difference between two tensions (Results, p. 12):
rate = (F2 - F1) / dx * v. Units: pN, nm, nm/s -> pN/s."""


def run(inputs, settings):
    return {"rate": (inputs["F2"] - inputs["F1"]) / inputs["dx"] * inputs["v"]}


def symbolic():
    import sympy as sp
    F1, F2, dx, v = sp.symbols("F1 F2 dx v", positive=True)
    return {"rate": (F2 - F1) / dx * v}
