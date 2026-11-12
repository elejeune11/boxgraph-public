# Myocyte profiles per capillary profile in the same cross sections.


def run(inputs, settings):
    return {"ratio": inputs["Nm"] / inputs["Nc"]}


def symbolic():
    import sympy as sp
    Nm, Nc = sp.symbols("Nm Nc", positive=True)
    return {"ratio": Nm / Nc}
