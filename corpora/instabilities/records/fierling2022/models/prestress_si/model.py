# SI p. 21: sigma_a = chi_2D (gamma - 1)/gamma, as printed.
# gamma is the factor on the Gram matrix of the unstrained facet (p. 20): the equilibrium area is
# gamma * A_i = A_0, so gamma = A_0/A_i = 1/(1 + epsilon_a) with the main text's epsilon_a.


def run(inputs, settings):
    gamma = 1.0 / (1.0 + inputs["eps"])
    return {"sigma_a": inputs["chi"] * (gamma - 1.0) / gamma}


def symbolic():
    import sympy as sp
    chi, eps = sp.symbols("chi eps", positive=True)
    gamma = 1 / (1 + eps)
    return {"sigma_a": chi * (gamma - 1) / gamma}
