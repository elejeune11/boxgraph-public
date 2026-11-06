# Eq. 5: p = c p0, for the motor stall force.


def run(inputs, settings):
    return {"Fm": inputs["c"] * inputs["Fm0"]}


def symbolic():
    import sympy as sp
    c, Fm0 = sp.symbols("c Fm0", positive=True)
    return {"Fm": c * Fm0}
