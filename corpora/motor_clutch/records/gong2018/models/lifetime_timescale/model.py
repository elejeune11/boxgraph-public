# tau_l = Fm Nm / (vu kl).  Ports: Fm pN, Nm 1, vu nm/s, kl pN/nm -> tau_l s.

def run(inputs, settings):
    return {"tau_l": inputs["Fm"] * inputs["Nm"] / (inputs["vu"] * inputs["kl"])}


def symbolic():
    import sympy as sp
    Fm, Nm, vu, kl = sp.symbols("Fm Nm vu kl", positive=True)
    return {"tau_l": Fm * Nm / (vu * kl)}
