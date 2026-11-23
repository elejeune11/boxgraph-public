# tau = G * gamma (Fig. S1, right: the line y = 185.07x). Units: kPa.


def run(inputs, settings):
    return {"tau": inputs["G"] * inputs["gamma"]}


def symbolic():
    import sympy as sp
    G, gamma = sp.symbols("G gamma", positive=True)
    return {"tau": G * gamma}
