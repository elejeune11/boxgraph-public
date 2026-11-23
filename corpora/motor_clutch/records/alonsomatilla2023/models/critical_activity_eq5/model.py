# Eq. 5: F_c-i^crit = C1 tau / (tau + 1).


def run(inputs, settings):
    return {"Fcrit": inputs["C1"] * inputs["tau"] / (inputs["tau"] + 1)}


def symbolic():
    import sympy as sp
    C1, tau = sp.symbols("C1 tau", positive=True)
    return {"Fcrit": C1 * tau / (tau + 1)}
