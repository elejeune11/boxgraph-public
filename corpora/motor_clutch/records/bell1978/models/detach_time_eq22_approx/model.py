import math

EV_ERG = 1.602176634e-12


def run(inputs, settings):
    Y0 = inputs["r0"] * 1e-7 * inputs["f"] / EV_ERG / inputs["kT"]  # nm*dyne -> erg -> eV
    return {"t": math.exp(-Y0) / (inputs["k_minus"] * (1 + Y0))}


def symbolic():
    import sympy as sp
    k_minus, r0, f, kT = sp.symbols("k_minus r0 f kT", positive=True)
    Y0 = r0 * 1e-7 * f / EV_ERG / kT
    return {"t": sp.exp(-Y0) / (k_minus * (1 + Y0))}
