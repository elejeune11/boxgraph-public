# sigma = E * eps (Fig. S1, left: the line y = 930.32x through the origin). Units: kPa.


def run(inputs, settings):
    return {"sigma": inputs["E"] * inputs["eps"]}


def symbolic():
    import sympy as sp
    E, eps = sp.symbols("E eps", positive=True)
    return {"sigma": E * eps}
