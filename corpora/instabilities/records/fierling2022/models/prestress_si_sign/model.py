# Variant of prestress_si: sigma_a = chi_2D (1 - gamma)/gamma, gamma = 1/(1 + epsilon_a).


def run(inputs, settings):
    gamma = 1.0 / (1.0 + inputs["eps"])
    return {"sigma_a": inputs["chi"] * (1.0 - gamma) / gamma}


def symbolic():
    import sympy as sp
    chi, eps = sp.symbols("chi eps", positive=True)
    gamma = 1 / (1 + eps)
    return {"sigma_a": chi * (1 - gamma) / gamma}
