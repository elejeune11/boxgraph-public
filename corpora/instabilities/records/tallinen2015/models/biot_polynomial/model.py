# The Biot point (p. 7): the real root g > 1 of g^6 - 3g^4 - g^2 - 1 = 0 (a cubic in g^2).
import numpy as np


def run(inputs, settings):
    roots = np.roots([1.0, -3.0, -1.0, -1.0])  # x = g^2
    x = max(r.real for r in roots if abs(r.imag) < 1e-12 and r.real > 1.0)
    return {"gb": float(np.sqrt(x))}
