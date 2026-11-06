# Eq. 5: p = c p0, for the clutch unloaded off-rate.


def run(inputs, settings):
    return {"koff": inputs["c"] * inputs["koff0"]}


def symbolic():
    import sympy as sp
    c, koff0 = sp.symbols("c koff0", positive=True)
    return {"koff": c * koff0}
