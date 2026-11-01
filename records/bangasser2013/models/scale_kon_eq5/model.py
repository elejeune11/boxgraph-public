# Eq. 5: p = c p0, for the clutch on-rate.


def run(inputs, settings):
    return {"kon": inputs["c"] * inputs["kon0"]}


def symbolic():
    import sympy as sp
    c, kon0 = sp.symbols("c kon0", positive=True)
    return {"kon": c * kon0}
