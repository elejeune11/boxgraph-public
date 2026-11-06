import math


def run(inputs, settings):
    return {"L": inputs["cu"] * inputs["rho"] * inputs["ls"] / (math.pi * inputs["R"] ** 2)}


def symbolic():
    import sympy as sp
    cu, rho, ls, R = sp.symbols("cu rho ls R", positive=True)
    return {"L": cu * rho * ls / (sp.pi * R**2)}
