# The balloon limit of Eq. 11 as printed on p. 3 (alpha << p-hat, alpha neglected):
#   kappa-hat_w^3 - 4 p-hat kappa-hat_w + 2 p-hat^2 = 0, smallest positive root.
import numpy as np


def run(inputs, settings):
    p = inputs["phat"]
    roots = np.roots([1.0, 0.0, -4 * p, 2 * p**2])
    real = sorted(r.real for r in roots if abs(r.imag) < 1e-12 * max(1.0, abs(r)) and r.real > 0)
    return {"khat_w": float(real[0]) if real else float("nan")}
