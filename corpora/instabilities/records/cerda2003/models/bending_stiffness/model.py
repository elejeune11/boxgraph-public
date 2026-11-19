# B = E t^3 / [12 (1 - nu^2)], in Pa, m -> N m.


def run(inputs, settings):
    E, t, nu = inputs["E"], inputs["t"], inputs["nu"]
    return {"B": E * t**3 / (12.0 * (1.0 - nu**2))}


def symbolic():
    import sympy as sp
    E, t, nu = sp.symbols("E t nu", positive=True)
    return {"B": E * t**3 / (12 * (1 - nu**2))}
