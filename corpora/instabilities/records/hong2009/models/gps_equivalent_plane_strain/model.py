import math


def run(inputs, settings):
    # Eq. 3: lambda_1 = lambda_1'/sqrt(lambda_2), so lambda_1' = lambda_1 sqrt(lambda_2); epsilon = 1 - lambda_1'
    return {"eps": 1 - inputs["lam1"] * math.sqrt(inputs["lam2"])}


def symbolic():
    import sympy as sp
    lam1, lam2 = sp.symbols("lam1 lam2", positive=True)
    return {"eps": 1 - lam1 * sp.sqrt(lam2)}
