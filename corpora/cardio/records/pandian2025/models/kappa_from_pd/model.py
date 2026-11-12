# kappa ~ Pd mu L / eps_p, all in SI as the paper gives them (Pd m/s, mu Pa s, L m); the number is taken as m^2.
# Dimensionally the right side is Pa m^2 (q_kappa_dimension); the formula is entered as printed.


def run(inputs, settings):
    return {"kappa": inputs["Pd"] * inputs["mu"] * inputs["L"] / inputs["eps"]}


def symbolic():
    import sympy as sp
    Pd, mu, L, eps = sp.symbols("Pd mu L eps", positive=True)
    return {"kappa": Pd * mu * L / eps}
