import math

EV_J = 1.602176634e-19
DALTON_KG = 1.66053906660e-27


def run(inputs, settings):
    # SI: r0 in m, E0 in J per molecule, m in kg
    r0 = inputs["r0"] * 1e-9
    E0 = inputs["E0"] * EV_J
    m = inputs["m"] * DALTON_KG
    return {"tau_h": 2 * math.pi * r0 * (E0 / m) ** -0.5}


def symbolic():
    import sympy as sp
    r0, E0, m = sp.symbols("r0 E0 m", positive=True)
    return {"tau_h": 2 * sp.pi * r0 * 1e-9 * (E0 * EV_J / (m * DALTON_KG)) ** sp.Rational(-1, 2)}
