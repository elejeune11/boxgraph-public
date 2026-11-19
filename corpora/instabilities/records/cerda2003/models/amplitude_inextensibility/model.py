# Constraint (2) with the periodic solution gives A_n^2 k_n^2 W/8 ≈ Delta (p. 2); with k = 2 pi/lambda,
# A = sqrt(8 Delta/W)/k = sqrt(8 Delta/W) lambda/(2 pi). SI units.
import math


def run(inputs, settings):
    k = 2.0 * math.pi / inputs["lam"]
    return {"A": math.sqrt(8.0 * inputs["Delta"] / inputs["W"]) / k}


def symbolic():
    import sympy as sp
    Delta, W, lam = sp.symbols("Delta W lam", positive=True)
    return {"A": sp.sqrt(8 * Delta / W) * lam / (2 * sp.pi)}
