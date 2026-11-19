# Eq. B 18, as printed (checked against the page image).
import math

R2 = math.sqrt(2.0)


def run(inputs, settings):
    L = inputs["L"]
    a = L / (2.0 * R2)
    num = 2.0 * R2 * math.exp(-a) * (4.0 * math.exp(a) * math.sin(L / R2) - math.exp(L / R2) * math.sin(a)
                                     - 3.0 * math.sin(3.0 * a) + (math.exp(L / R2) - 1.0) * math.cos(a))
    den = 5.0 * (math.exp(L / R2) + (R2 * L - 1.0) * math.sin(L / R2) - math.cos(L / R2))
    return {"B": num / den}


def symbolic():
    import sympy as sp
    L = sp.symbols("L", positive=True)
    r2 = sp.sqrt(2)
    a = L / (2 * r2)
    num = 2 * r2 * sp.exp(-a) * (4 * sp.exp(a) * sp.sin(L / r2) - sp.exp(L / r2) * sp.sin(a)
                                 - 3 * sp.sin(3 * a) + (sp.exp(L / r2) - 1) * sp.cos(a))
    den = 5 * (sp.exp(L / r2) + (r2 * L - 1) * sp.sin(L / r2) - sp.cos(L / r2))
    return {"B": num / den}
