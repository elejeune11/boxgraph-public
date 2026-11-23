# E = 2 (1 + nu) G; G in kPa, E in MPa.


def run(inputs, settings):
    return {"E": 2.0 * (1.0 + inputs["nu"]) * inputs["G"] / 1000.0}


def symbolic():
    import sympy as sp
    G, nu = sp.symbols("G nu", positive=True)
    return {"E": 2 * (1 + nu) * G / 1000}
