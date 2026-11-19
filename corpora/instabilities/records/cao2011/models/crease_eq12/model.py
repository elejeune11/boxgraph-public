# Eq. 1.2: with lambda_1 lambda_2 lambda_3 = 1 and lambda_1/lambda_2 = q, lambda_1^2 = q/lambda_3.
import math


def run(inputs, settings):
    coef = math.sqrt(inputs["ratio"])
    return {"coef": coef, "eps_C": 1.0 - coef / math.sqrt(inputs["lam3"])}


def symbolic():
    import sympy as sp
    ratio, lam3 = sp.symbols("ratio lam3", positive=True)
    return {"coef": sp.sqrt(ratio), "eps_C": 1 - sp.sqrt(ratio) / sp.sqrt(lam3)}
