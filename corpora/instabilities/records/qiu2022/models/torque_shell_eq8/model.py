# Eq. 8, shell normalization: M-bar = pi [kappa-bar - kappa-bar^3 / (8 (1 + p-bar/3))]
import math


def run(inputs, settings):
    k, p = inputs["kbar"], inputs["pbar"]
    return {"Mbar": math.pi * (k - k**3 / (8 * (1 + p / 3)))}


def symbolic():
    import sympy as sp
    kbar, pbar = sp.symbols("kbar pbar", positive=True)
    return {"Mbar": sp.pi * (kbar - kbar**3 / (8 * (1 + pbar / 3)))}
