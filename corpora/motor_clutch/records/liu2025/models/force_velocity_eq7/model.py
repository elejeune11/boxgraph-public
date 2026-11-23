# Linear force-velocity relation of the myosin II motors (Eq. 7), as printed.
def run(inputs, settings):
    return {"v": inputs["v0"] * (1.0 - inputs["Fm"] / (inputs["Nm"] * inputs["Fst"]))}


def symbolic():
    import sympy as sp
    v0, Fm, Nm, Fst = sp.symbols("v0 Fm Nm Fst", positive=True)
    return {"v": v0 * (1 - Fm / (Nm * Fst))}
