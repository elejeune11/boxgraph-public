# CO [L/min] = HR [1/min] x EF x Vmax [mL] / 1000.


def run(inputs, settings):
    return {"CO": inputs["HR"] * inputs["EF"] * inputs["Vmax"] / 1000.0}


def symbolic():
    import sympy as sp
    HR, EF, Vmax = sp.symbols("HR EF Vmax", positive=True)
    return {"CO": HR * EF * Vmax / 1000}
