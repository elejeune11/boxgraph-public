# Eq. 4 (first line): SR = S x R.


def run(inputs, settings):
    return {"SR": inputs["S"] * inputs["R"]}


def symbolic():
    import sympy as sp
    S, R = sp.symbols("S R")
    return {"SR": S * R}
