import math


def run(inputs, settings):
    r, h, E, dz = inputs["r"], inputs["h"], inputs["E"], inputs["dz"]
    a = r / h
    cp = 3 * math.pi * r**2 * (a + 1) ** 2 / (E * (2 * a + 1))
    return {"C": cp * dz, "Cp": cp}


def symbolic():
    import sympy as sp
    r, h, E, dz = sp.symbols("r h E dz", positive=True)
    a = r / h
    cp = 3 * sp.pi * r**2 * (a + 1) ** 2 / (E * (2 * a + 1))
    return {"C": cp * dz, "Cp": cp}
