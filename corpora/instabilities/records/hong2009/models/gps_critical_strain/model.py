import math


def run(inputs, settings):
    # Eq. 3: lambda_1 = lambda_1'/sqrt(lambda_2), with lambda_1' = 1 - eps; the strain along 1 is 1 - lambda_1
    return {"eps1": 1 - (1 - inputs["eps"]) / math.sqrt(inputs["lam2"])}


def symbolic():
    import sympy as sp
    eps, lam2 = sp.symbols("eps lam2", positive=True)
    return {"eps1": 1 - (1 - eps) / sp.sqrt(lam2)}
