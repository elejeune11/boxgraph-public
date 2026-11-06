import math


def run(inputs, settings):
    return {"L1": 8 * inputs["lambda_q"] * inputs["rho"] * inputs["Lv"] / (math.pi * inputs["R"] ** 2)}


def symbolic():
    import sympy as sp
    lambda_q, rho, Lv, R = sp.symbols("lambda_q rho Lv R", positive=True)
    return {"L1": 8 * lambda_q * rho * Lv / (sp.pi * R**2)}
