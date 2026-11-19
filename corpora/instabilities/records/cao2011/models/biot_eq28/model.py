# Eq. 2.8: the real root of r^3 - 3r^2 - r - 1 = 0, r = lambda_2/lambda_1; with lambda_1 lambda_2
# lambda_3 = 1, lambda_1^2 r lambda_3 = 1, so lambda_W = 1/sqrt(r lambda_3) (Eq. 1.1).
import math

import numpy as np


def root():
    roots = np.roots([1.0, -3.0, -1.0, -1.0])
    real = [z.real for z in roots if abs(z.imag) < 1e-12]
    return float(max(real))


def run(inputs, settings):
    r = root()
    lam_w = 1.0 / math.sqrt(r * inputs["lam3"])
    return {"r": r, "ratio": 1.0 / r, "coef": 1.0 / math.sqrt(r), "eps_W": 1.0 - lam_w}
