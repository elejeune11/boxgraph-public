import math


def run(inputs, settings):
    return {"tau0": inputs["tau_f0"] * math.exp(-inputs["E0"] / inputs["kT"])}


def symbolic():
    import sympy as sp
    tau_f0, E0, kT = sp.symbols("tau_f0 E0 kT", positive=True)
    return {"tau0": tau_f0 * sp.exp(-E0 / kT)}
