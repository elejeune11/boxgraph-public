K_B_EV = 8.617333262e-5  # Boltzmann constant, eV/K (CODATA, exact SI)


def run(inputs, settings):
    return {"kT": K_B_EV * (inputs["T"] + 273.15)}


def symbolic():
    import sympy as sp
    T = sp.symbols("T", positive=True)
    return {"kT": K_B_EV * (T + 273.15)}
