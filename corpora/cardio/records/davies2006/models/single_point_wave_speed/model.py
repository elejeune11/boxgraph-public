# c = (1/rho) sqrt(sum dP^2 / sum dU^2), SI units: sqrt(Pa^2 / (m/s)^2) / (kg/m^3) = m/s.
import math


def run(inputs, settings):
    return {"c": math.sqrt(inputs["sum_dP2"] / inputs["sum_dU2"]) / inputs["rho"]}


def symbolic():
    import sympy as sp
    sum_dP2, sum_dU2, rho = sp.symbols("sum_dP2 sum_dU2 rho", positive=True)
    return {"c": sp.sqrt(sum_dP2 / sum_dU2) / rho}
