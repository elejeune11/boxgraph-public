# v = 0.4 D - 1.9, D in um, v in mm/s, as printed.


def run(inputs, settings):
    return {"v": 0.4 * inputs["D"] - 1.9}


def symbolic():
    import sympy as sp
    D = sp.symbols("D", positive=True)
    return {"v": sp.Float("0.4") * D - sp.Float("1.9")}
