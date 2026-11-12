# HRR = HRmax - HRrest, all in beats per minute (1/min).


def run(inputs, settings):
    return {"HRR": inputs["HRmax"] - inputs["HRrest"]}


def symbolic():
    import sympy as sp
    HRmax, HRrest = sp.symbols("HRmax HRrest", positive=True)
    return {"HRR": HRmax - HRrest}
