# Eq. 3.3 (= Eq. B15), divided by sin(Theta): K^2 / sin(Theta) = 8 sqrt2 / D(Lambda),
# D = 1 + exp(-L/sqrt2) [(sqrt2 L - 1) sin(L/sqrt2) - cos(L/sqrt2)]. Output: K / sqrt(sin Theta).
import math

R2 = math.sqrt(2.0)


def run(inputs, settings):
    L = inputs["L"]
    D = 1.0 + math.exp(-L / R2) * ((R2 * L - 1.0) * math.sin(L / R2) - math.cos(L / R2))
    return {"Ks": math.sqrt(8.0 * R2 / D)}


def symbolic():
    import sympy as sp
    L = sp.symbols("L", positive=True)
    r2 = sp.sqrt(2)
    D = 1 + sp.exp(-L / r2) * ((r2 * L - 1) * sp.sin(L / r2) - sp.cos(L / r2))
    return {"Ks": sp.sqrt(8 * r2 / D)}
