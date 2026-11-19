# Eq. 3.13 as printed, with u^(n)_1(x1, 0) = l f(0) sin(n k x1) (Eq. 2.10), f(0) = (r - 1)/(r + 1) from (2.9):
# Int_0^l xibar_n l cos(nkx1) * xi_n l f(0) nk cos(nkx1) dx1 = pi n f(0) l^2 xibar_n xi_n,
# so with the printed prefactor l (r-1)^2 (taking l = 1): K = pi (r - 1)^2 f(0).
import math


def run(inputs, settings):
    r = inputs["r"]
    f0 = (r - 1.0) / (r + 1.0)
    return {"K": math.pi * (r - 1.0) ** 2 * f0}


def symbolic():
    import sympy as sp
    r = sp.symbols("r", positive=True)
    return {"K": sp.pi * (r - 1) ** 2 * (r - 1) / (r + 1)}
