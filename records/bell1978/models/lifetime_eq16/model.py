import math

EV_ERG = 1.602176634e-12


def run(inputs, settings):
    # nm * dyne -> erg is 1e-7; erg -> eV divides by 1.602176634e-12
    gamma_f = inputs["gamma"] * 1e-7 * inputs["f"] / EV_ERG
    return {"tau": inputs["tau0"] * math.exp((inputs["E0"] - gamma_f) / inputs["kT"])}


def symbolic():
    import sympy as sp
    tau0, E0, gamma, f, kT = sp.symbols("tau0 E0 gamma f kT", positive=True)
    return {"tau": tau0 * sp.exp((E0 - gamma * 1e-7 * f / EV_ERG) / kT)}
