# ln(1/eps), the factor of Eqs. 28-31; and its change when eps is multiplied by m:
# fold = ln(1/eps) / ln(1/(m eps)).
import math


def run(inputs, settings):
    L = math.log(1 / inputs["eps"])
    return {"L": L, "fold": L / math.log(1 / (inputs["m"] * inputs["eps"]))}


def symbolic():
    import sympy as sp
    eps, m = sp.symbols("eps m", positive=True)
    L = sp.log(1 / eps)
    return {"L": L, "fold": L / sp.log(1 / (m * eps))}
