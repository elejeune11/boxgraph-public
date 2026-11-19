# Eq. 7 as printed.


def run(inputs, settings):
    return {"lam_over_H": 3.5 * (1.0 - inputs["eM"])}


def symbolic():
    import sympy as sp
    eM = sp.symbols("eM", positive=True)
    return {"lam_over_H": 3.5 * (1 - eM)}
