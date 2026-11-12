# tau_w = 4 mu v / r; v in um/s and r in um (the 1e-6 factors cancel); Pa -> dyn/cm^2 is x10.


def run(inputs, settings):
    return {"tau_w": 4.0 * inputs["mu"] * inputs["v"] / inputs["r"] * 10.0}


def symbolic():
    import sympy as sp
    v, r, mu = sp.symbols("v r mu", positive=True)
    return {"tau_w": 40 * mu * v / r}
