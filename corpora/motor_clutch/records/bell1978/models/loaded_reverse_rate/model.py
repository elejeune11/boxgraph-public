import math

EV_ERG = 1.602176634e-12


def run(inputs, settings):
    # nm * dyne -> erg is 1e-7; erg -> eV divides by 1.602176634e-12
    gamma_f = inputs["gamma"] * 1e-7 * inputs["f"] / EV_ERG
    return {"k_minus_F": inputs["k_minus"] * math.exp(gamma_f / inputs["kT"])}


def symbolic():
    import sympy as sp
    k_minus, gamma, f, kT = sp.symbols("k_minus gamma f kT", positive=True)
    return {"k_minus_F": k_minus * sp.exp(gamma * 1e-7 * f / EV_ERG / kT)}
