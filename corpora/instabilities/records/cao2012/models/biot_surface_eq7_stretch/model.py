import math

# Eq. 7, eW = 1 - c/sqrt(lambda_3), with Eq. 4, eW = 1 - lambda_1:  lambda_1 = c/sqrt(lambda_3).


def run(inputs, settings):
    return {"lam1": inputs["c"] / math.sqrt(inputs["lam3"])}


def symbolic():
    import sympy as sp
    c, lam3 = sp.symbols("c lam3", positive=True)
    return {"lam1": c / sp.sqrt(lam3)}
