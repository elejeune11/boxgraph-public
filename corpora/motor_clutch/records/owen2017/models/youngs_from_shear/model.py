# E = 2 G (1 + nu), isotropic linear elasticity.


def run(inputs, settings):
    return {"E": 2.0 * inputs["G"] * (1.0 + inputs["nu"])}


def symbolic():
    import sympy as sp
    G, nu = sp.symbols("G nu", positive=True)
    return {"E": 2 * G * (1 + nu)}
