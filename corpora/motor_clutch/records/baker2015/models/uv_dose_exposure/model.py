# UV dose (radiant exposure) = intensity x time. Ports: I in mW/cm^2, t in s, dose in mJ/cm^2.


def run(inputs, settings):
    return {"dose": inputs["I"] * inputs["t"]}


def symbolic():
    import sympy as sp
    I, t = sp.symbols("I t", positive=True)
    return {"dose": I * t}
