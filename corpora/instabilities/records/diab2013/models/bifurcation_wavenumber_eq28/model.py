# Eq. 2.8 (p. 5): normalized bifurcation wavenumber kbar = k/a of the flat EDM neo-Hookean surface
# under plane-strain compression, with lambda = 1 - eps (p. 5).
import math


def run(inputs, settings):
    lam = 1.0 - inputs["eps"]
    num = 4 * lam**2 * math.sqrt(3 - 2 * lam**4 - lam**8)
    den = (lam**6 - lam**4 + 3 * lam**2 + 1) * (lam**3 + lam**2 + lam - 1) * (lam**3 - lam**2 + lam + 1)
    return {"kbar": num / den}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    lam = 1 - eps
    num = 4 * lam**2 * sp.sqrt(3 - 2 * lam**4 - lam**8)
    den = (lam**6 - lam**4 + 3 * lam**2 + 1) * (lam**3 + lam**2 + lam - 1) * (lam**3 - lam**2 + lam + 1)
    return {"kbar": num / den}
