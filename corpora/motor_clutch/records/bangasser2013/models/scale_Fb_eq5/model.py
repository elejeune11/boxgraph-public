# Eq. 5: p = c p0, for the clutch bond rupture force.


def run(inputs, settings):
    return {"Fb": inputs["c"] * inputs["Fb0"]}


def symbolic():
    import sympy as sp
    c, Fb0 = sp.symbols("c Fb0", positive=True)
    return {"Fb": c * Fb0}
