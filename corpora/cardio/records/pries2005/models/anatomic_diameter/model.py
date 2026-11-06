# A layer of thickness W on each side of the wall: D_anatomic = D_tube + 2 W (all in um).


def run(inputs, settings):
    return {"D": inputs["D_tube"] + 2.0 * inputs["W"]}


def symbolic():
    import sympy as sp
    Dt, W = sp.symbols("D_tube W", positive=True)
    return {"D": Dt + 2 * W}
