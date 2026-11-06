# Eq. 5: p = c p0, for the motor unloaded velocity.


def run(inputs, settings):
    return {"vu": inputs["c"] * inputs["vu0"]}


def symbolic():
    import sympy as sp
    c, vu0 = sp.symbols("c vu0", positive=True)
    return {"vu": c * vu0}
