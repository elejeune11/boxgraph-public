# Vmin = Vmax (1 - EF); mL.


def run(inputs, settings):
    return {"Vmin": inputs["Vmax"] * (1.0 - inputs["EF"])}


def symbolic():
    import sympy as sp
    Vmax, EF = sp.symbols("Vmax EF", positive=True)
    return {"Vmin": Vmax * (1 - EF)}
