# Port of the header comment of Surface_Evolver_script.txt (line 1): h = sqrt(12 (1 - nu^2) kappa / Y), in units of R_DV.
import math


def run(inputs, settings):
    h_nd = math.sqrt(12 * (1 - inputs["nu"] ** 2) * inputs["kappa"] / inputs["Y"])
    return {"h": h_nd * inputs["R_DV"]}


def symbolic():
    import sympy as sp
    Y, kappa, R = sp.symbols("Y kappa R_DV", positive=True)
    nu = sp.Symbol("nu")
    return {"h": sp.sqrt(12 * (1 - nu**2) * kappa / Y) * R}
