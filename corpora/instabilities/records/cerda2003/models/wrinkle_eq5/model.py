# Eq. 5: lambda = 2 sqrt(pi) (B/T)^(1/4) L^(1/2); A = sqrt(2)/pi (Delta/W)^(1/2) lambda. SI units.
import math


def run(inputs, settings):
    B, T, L = inputs["B"], inputs["T"], inputs["L"]
    lam = 2.0 * math.sqrt(math.pi) * (B / T) ** 0.25 * math.sqrt(L)
    A = math.sqrt(2.0) / math.pi * math.sqrt(inputs["Delta"] / inputs["W"]) * lam
    return {"lam": lam, "A": A}


def symbolic():
    import sympy as sp
    B, T, L, Delta, W = sp.symbols("B T L Delta W", positive=True)
    lam = 2 * sp.sqrt(sp.pi) * (B / T) ** sp.Rational(1, 4) * sp.sqrt(L)
    return {"lam": lam, "A": sp.sqrt(2) / sp.pi * sp.sqrt(Delta / W) * lam}
