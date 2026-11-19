# Eq. 11, balloon normalization: the smallest positive root kappa-hat_w of
#   8 (alpha^2 + p-hat/3) (p-hat/2 + 2 alpha - kappa-hat_w) + (2 kappa-hat_w/3 - 4 alpha) kappa-hat_w^2 = 0
import numpy as np


def smallest_positive_root(alpha, phat):
    c = 8 * (alpha**2 + phat / 3)
    roots = np.roots([2 / 3, -4 * alpha, -c, c * (phat / 2 + 2 * alpha)])
    real = sorted(r.real for r in roots if abs(r.imag) < 1e-12 * max(1.0, abs(r)) and r.real > 0)
    return float(real[0]) if real else float("nan")


def run(inputs, settings):
    return {"khat_w": smallest_positive_root(inputs["alpha"], inputs["phat"])}
