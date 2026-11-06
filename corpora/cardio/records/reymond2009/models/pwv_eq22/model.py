# Eq. 22: PWV = a2 / d^b2, with d in mm and PWV in m/s (q_eq22_units).


def run(inputs, settings):
    return {"PWV": inputs["a2"] / inputs["d"] ** inputs["b2"]}


def symbolic():
    import sympy as sp
    d, a2, b2 = sp.symbols("d a2 b2", positive=True)
    return {"PWV": a2 / d ** b2}
