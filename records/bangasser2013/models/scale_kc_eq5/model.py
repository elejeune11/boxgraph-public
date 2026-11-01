# Eq. 5: p = c p0, for the clutch spring constant.


def run(inputs, settings):
    return {"kc": inputs["c"] * inputs["kc0"]}


def symbolic():
    import sympy as sp
    c, kc0 = sp.symbols("c kc0", positive=True)
    return {"kc": c * kc0}
