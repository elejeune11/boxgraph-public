# Kf and E in the same unit (MPa) cancel; L0 in cm is 10 * L0 in mm, so L0^4 in mm^4 is 1e4 * L0^4.
def run(inputs, settings):
    L0_mm = 10.0 * inputs["L0"]
    return {"kf": inputs["Kf"] * L0_mm ** 4 / (inputs["E"] * inputs["I"])}


def symbolic():
    import sympy as sp
    Kf, L0, E, I = sp.symbols("Kf L0 E I", positive=True)
    return {"kf": Kf * (10 * L0) ** 4 / (E * I)}
