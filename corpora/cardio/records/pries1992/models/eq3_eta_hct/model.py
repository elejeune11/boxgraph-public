# Eq. 3 of the paper: all ports dimensionless.


def run(inputs, settings):
    B, C, H = inputs["B"], inputs["C"], inputs["HctD"]
    return {"eta": 1.0 + B * ((1.0 - H) ** C - 1.0)}


def symbolic():
    import sympy as sp
    B, C, H = sp.symbols("B C HctD")
    return {"eta": 1 + B * ((1 - H) ** C - 1)}
